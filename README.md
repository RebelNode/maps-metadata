Maps metadata
=============

This repository contains metadata for maps used in Beyond All Reason game.

It contains files that work as source of truth that is then used by different
components in the BAR infrastructure, and build scripts that manipulate and
validate that information.

For more convenient data input, the source of truth resigning in `map_list.yaml`
file is actually automatically generated by data export from BAR's
[Rowy](https://www.rowy.io/) instance: https://rowy.beyondallreason.dev/.
See [scripts/js/src/update_from_rowy.ts](scripts/js/src/update_from_rowy.ts).

Development
-----------

Mostly, you modify the source of truth files, commit via pull request and
it gets deployed via GitHub Actions workflow.

When you are changing scripts, it's useful to be able to regenerate files
manually and check if all is working correctly. It's possible to do it in two
different ways:
- directly (Linux or in WSL): preferred for development as editor has an easy
  access to everything
- inside a Docker container: primarily for hermetic testing

### Local environment

Make sure you have python, curl, Node.js and unzip installed (see Dockerfile for
the full list of dependencies), and then run install script to setup an isolated
environment for the development.

Note: You need version 18.18 of Node.js. This is easiest to get using Node Version Manager https://github.com/nvm-sh/nvm and then run

```
nvm install 18.18
nvm use 18.18
```

```
./scripts/install.sh
```

Then we need to setup a few environment variables to make sure that installed
dependencies are correctly visible in `PATH`

```
source .envrc
```

Hint: `.envrc` is a [direnv](https://direnv.net/) compatible file.

To make sure that your editor is correctly resolving all types (e.g. generate
TypeScript type definitions from JSON Schema), make sure to run

```
make types
```

### Docker environment

Build image with current version of the code, it does basically what steps above
but in a docker container.

```
docker build . -t maps-metadata-build
```

Get into the docker container shell

```
docker run -it --rm maps-metadata-build
```

Note: if you later need to copy some files *out* of the docker container, read
about `docker cp`.

### Build artifacts

Generation of output files is done using Makefile, so run

```
make -j $(nproc)
```

to regenerate all files in the `gen/` directory, and then

```
make -j $(nproc) test
```

to run additional checks on them.

To cleanup generated files, simply run `make clean`.

Documentation
-------------

See GitHub wiki for more documentation.
