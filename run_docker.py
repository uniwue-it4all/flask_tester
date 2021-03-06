from pathlib import Path
from subprocess import run as subprocess_run

from docker import from_env as docker_client_from_env, DockerClient
from docker.models.containers import Container
from docker.types import Mount


class BindMount(Mount):
    def __init__(self, source: Path, target: str, read_only: bool = False):
        super().__init__(source=str(source.absolute()), target=target, read_only=read_only, type="bind")


max_runtime_seconds: int = 30

build_image: bool = True

tester_image_name: str = "flask_tester"
exercise_name: str = "login"
result_file_name: str = "result.json"

exercise_path: Path = Path.cwd() / exercise_name
result_file_path: Path = Path.cwd() / "results" / result_file_name

# clear result and logs files
if result_file_path.exists():
    result_file_path.unlink()

result_file_path.touch()

# running...
client: DockerClient = docker_client_from_env()

# build server and tester image if requested.
if build_image:
    subprocess_run(f"docker build -t {tester_image_name} .", shell=True)
    # client.images.build(tag=tester_image_name, path=".")

    subprocess_run("docker image prune -f", shell=True)
    # client.images.prune()

print("Running tester container!")
tester_container: Container = client.containers.run(
    image=tester_image_name,
    mounts=[
        BindMount(source=result_file_path, target=f"/data/{result_file_name}"),
        BindMount(source=exercise_path / "app", target=f"/data/app", read_only=True),
        BindMount(source=exercise_path / "testConfig.json", target="/data/testConfig.json", read_only=True),
        BindMount(source=exercise_path / "test_login.py", target="/data/test_login.py", read_only=True),
    ],
    detach=True,
)

# stop and remove tester container
tester_container.wait(timeout=max_runtime_seconds)

#if client.containers.get(tester_container.id):
#    tester_container.remove()
