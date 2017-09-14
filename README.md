# python-snmp-datasource

## Usage

A wrapper over `snmpget` that supports configuration via inputfile.
Input via `stdin` and output via `stdout` are symmetrical.

### Invocation

```console
cat test.txt | snmp_datasource.py
```

Where [test.txt](./test.txt) is an example file.


By using [go-stdin-sleep-stdout](https://github.com/docktermj/go-stdin-sleep-stdout),
a more sophisticated test is this:

```console
cat test.txt | ./snmp_datasource.py | go-stdin-sleep-stdout --sleep 1 | ./snmp_datasource.py
```

The SNMP metrics returned in `stdout` can be piped to the `stdin` of a subsequent invocation of `snmp_datasource.py`.

## Development

### Dependencies

#### Set environment variables

```console
export PROJECT_DIR="${HOME}/docktermj.git"
export REPOSITORY_DIR="${PROJECT_DIR}/python-snmp-datasource"
```

#### Download project

```console
mkdir -p ${PROJECT_DIR}
cd ${PROJECT_DIR}
git clone git@github.com:docktermj/python-snmp-datasource.git
```