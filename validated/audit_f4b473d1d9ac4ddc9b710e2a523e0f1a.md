## Analysis

The external report concerns the absence of Seccomp-BPF syscall filtering in a sandboxed process that only relies on coarser-grained isolation (SELinux in the original report). orb-core has a directly analogous architecture: process-based "agents" that handle externally-influenced/untrusted data (QR-code decoding, iris/face biometric model inference) are isolated only via Linux namespaces, with no syscall filtering at all.

### Title
Process-based agent sandbox lacks Seccomp-BPF syscall filtering, leaving biometric-data-handling and untrusted-input-parsing agents with unrestricted kernel attack surface - (File: agentwire/src/agent/process.rs)

### Summary
orb-core isolates untrusted or crash-prone workloads (QR-code decoding, iris/face biometric model inference) in dedicated OS processes via the `agentwire` framework's `Process` trait. Sandboxing of these child processes is implemented solely with `unshare(CLONE_NEWUSER | CLONE_NEWIPC)` (optionally `CLONE_NEWNET`) and closing of unneeded file descriptors — there is no Seccomp-BPF (or any syscall) filter anywhere in the codebase. If an attacker can achieve arbitrary code execution inside one of these processes (e.g., via a memory-safety bug in the QR/MECARD decoding path fed by a malicious QR code, or in image/model inference feeding on attacker-influenced frames), the compromised process retains the full native syscall surface of the kernel, which is a large attack surface for kernel exploitation and sandbox escape.

### Finding Description
Process-based agents are spawned through `Process::spawn_process` / `spawn_process_impl`, which invokes `sandbox_agent()` as a `pre_exec` hook before `execve`: [1](#0-0) 

This function only calls `unshare` with `CLONE_NEWUSER | CLONE_NEWIPC` (and `CLONE_NEWNET` under the `sandbox-network` feature). It does not install any Seccomp filter, and a search of the whole repository confirms there is no `seccomp` usage anywhere in the codebase. The only other hardening applied to these processes is closing inherited file descriptors: [2](#0-1) 

This sandboxing primitive is used for security- and correctness-sensitive agents that consume externally influenced data:
- The `qr-code` agent decodes raw camera frames with the `rxing` QR library and parses payloads that later feed MECARD Wi-Fi credential parsing and signup/session QR parsing: [3](#0-2) [4](#0-3) 
- `mega-agent-one`/`mega-agent-two` run the iris, occlusion, IR-Net, RGB-Net, and face-identifier Python/native models over camera frames captured during a signup, producing iris codes, mask codes, and face-identifier fraud-check/self-custody results that are consumed by the biometric pipeline: [5](#0-4) 

All of these processes communicate with the main orb-core process (the broker) over a shared-memory IPC port (`agentwire::port`), which is how the biometric pipeline receives the iris/face-identifier output back into the trusted process: [6](#0-5) 

Because namespace unsharing (`CLONE_NEWUSER`/`CLONE_NEWIPC`/optionally `CLONE_NEWNET`) restricts *what resources* a process can see, but not *which syscalls* it can issue, a memory-corruption bug in the QR decoding library, MECARD parser, or a native/Python model inference path that is reachable from attacker-controlled input (a malicious QR code shown to the camera, or a crafted image) could be leveraged to obtain arbitrary code execution inside the sandboxed process with the entire native syscall table available. From there, an attacker could attempt to exploit a kernel vulnerability to escape the namespace sandbox entirely, or — without even needing a kernel bug — use unrestricted syscalls (e.g., `ptrace`, arbitrary `open`/`mmap` on `/proc`, network syscalls if `CLONE_NEWNET` isn't applied for that build) to interact with or corrupt the shared-memory IPC channel used to hand off iris codes and face-identifier fraud-check results to the trusted broker process, corrupting or forging the biometric pipeline results consumed during a signup.

### Impact Explanation
The lack of Seccomp filtering widens the practical impact of any single memory-safety bug in the sandboxed QR/MECARD parsing path or biometric model-inference path from "process crash/DoS" to "potential arbitrary code execution with unrestricted kernel syscall access." Given that `mega-agent-one`/`mega-agent-two` directly compute and hold the iris codes, mask codes, and face-identifier fraud-check outputs that determine signup uniqueness and fraud decisions, and that they communicate these results to the trusted broker over shared memory IPC, an attacker escalating from code execution in these agents could tamper with or exfiltrate biometric data, or corrupt the fraud/liveness decision fed back into the signup pipeline, leading to misattributed signups or fraud-check bypass.

### Likelihood Explanation
Exploitation requires first finding and triggering a memory-safety vulnerability in one of the externally-input-driven parsing/inference paths (QR/MECARD decoding or model inference) — a difficulty in itself. However, the sandbox architecture provides no additional mitigation once such a bug is found: since there is no seccomp filter at all, the attacker's post-exploitation capability is limited only by the two/three unshared namespaces, not by any restriction on the syscalls it can issue. This raises the severity conditional on any code-execution bug being found in these agents, matching the "High difficulty, high extra-mitigation-value" characterization in the original report.

### Recommendation
Add a Seccomp-BPF filter (e.g., via the `seccompiler`/`libseccomp` crate) to `sandbox_agent()` in `agentwire/src/agent/process.rs`, applied for every process-based agent (`qr-code`, `mega-agent-one`, `mega-agent-two`, `rgb-camera-worker`, `thermal-camera`), allow-listing only the syscalls actually required for each agent's runtime (image decoding, Python/CUDA inference, IPC via shared memory). Regenerate/audit the allow-list whenever these agents' dependencies (rxing, PyO3, ONNX/TensorRT runtimes, etc.) are upgraded, since new dependency versions may introduce new required syscalls.

### Proof of Concept
1. Inspect `agentwire/src/agent/process.rs::sandbox_agent` — it is the only isolation primitive applied via `pre_exec` before `execve`, and it consists solely of `unshare(CLONE_NEWUSER | CLONE_NEWIPC[| CLONE_NEWNET])`.
2. Grep the entire repository for `seccomp`: zero matches — confirming no syscall filtering exists on any process-based agent, including `qr-code` (which decodes untrusted external QR data) and `mega-agent-one`/`mega-agent-two` (which process signup biometric frames and produce iris/face-identifier outputs consumed by `src/plans/biometric_pipeline/mod.rs`).
3. Conceptually: if a vulnerability were found in the `rxing` QR decoder invoked at `src/agents/qr_code.rs:78-83` (`decode_rxing`), a crafted QR code shown to the RGB camera could achieve code execution inside the `qr-code` sandboxed process; with no seccomp filter, the attacker's payload has the full native syscall surface (e.g., `ptrace`, arbitrary filesystem/network syscalls not blocked by the unshared namespaces) available for further exploitation, rather than being constrained to a minimal allow-listed set.

### Citations

**File:** agentwire/src/agent/process.rs (L287-293)
```rust
                .pre_exec(sandbox_agent)
                .pre_exec(move || {
                    close_open_fds(libc::STDERR_FILENO + 1, &child_fds);
                    Ok(())
                })
                .spawn()
                .expect("failed to spawn a sub-process")
```

**File:** agentwire/src/agent/process.rs (L339-350)
```rust
fn sandbox_agent() -> std::io::Result<()> {
    #[allow(unused_mut)]
    let mut flags = CloneFlags::CLONE_NEWUSER | CloneFlags::CLONE_NEWIPC;
    #[cfg(feature = "sandbox-network")]
    {
        flags |= CloneFlags::CLONE_NEWNET;
    }
    match unshare(flags) {
        Ok(()) => Ok(()),
        Err(err) => Err(err.into()),
    }
}
```

**File:** src/agents/qr_code.rs (L72-99)
```rust
    fn run(self, mut port: RemoteInner<Self>) -> Result<(), Self::Error> {
        let mut qr_scanner = QrReader;
        loop {
            let input = port.recv();
            match input.value {
                ArchivedInput::Frame(frame) => {
                    match decode_rxing(
                        &mut qr_scanner,
                        frame.data().to_vec(),
                        frame.width(),
                        frame.height(),
                    ) {
                        Ok(output) => {
                            tracing::debug!("Decoded QR-code with rxing: {:?}", output.payload);
                            let chain = input.chain_fn();
                            port.try_send(&chain(output));
                        }
                        Err(e) => {
                            if !matches!(e, rxing::Exceptions::NotFoundException(_)) {
                                tracing::debug!("rxing error: {}", e);
                            }
                        }
                    }
                }
                ArchivedInput::Als(_) => {}
            }
        }
    }
```

**File:** src/network/mecard.rs (L77-127)
```rust
impl Credentials {
    /// Parses WiFi credentials encoded in MECARD format.
    pub fn parse(input: &str) -> IResult<&str, Self> {
        let (mut input, _) = tag("WIFI:")(input)?;

        // Parses a set of fields with the following requirements:
        // 1. A field is parsed no more than once.
        // 2. Fields are parsed in arbitrary order.
        // 3. Each field is optional.
        macro_rules! parse_fields {
            ($($parse:path => $opt:ident,)*) => {
                $(let mut $opt = None;)*
                loop {
                    $(
                        if $opt.is_none() {
                            if let Ok((next_input, parsed)) = $parse(input) {
                                $opt = Some(parsed);
                                input = next_input;
                                continue;
                            }
                        }
                    )*
                    break;
                }
            };
        }
        parse_fields! {
            AuthType::parse => auth_type,
            parse_ssid => ssid,
            parse_password => password,
            parse_hidden => hidden,
        }

        let ssid = ssid.filter(|ssid| !ssid.is_empty());
        let (password, auth_type) = password
            .filter(|pwd| !pwd.is_empty())
            .map_or((None, Some(AuthType::Nopass)), |pwd| (Some(Password(pwd)), auth_type));

        // ssid is actually not optional.
        if ssid.is_none() {
            let (_, ()) = fail(input)?;
        }

        let (input, _) = tag(";")(input)?;
        let (input, _) = eof(input)?;

        let auth_type = auth_type.unwrap_or_default();
        let ssid = ssid.unwrap_or_default();
        let hidden = hidden.unwrap_or_default();
        Ok((input, Self { auth_type, ssid, password, hidden }))
    }
```

**File:** src/plans/biometric_pipeline/mod.rs (L338-390)
```rust
                ModelOutput::MegaAgentOne(output) => {
                    match output {
                        mega_agent_one::Output::Config(config) => {
                            mega_agent_one_config = Some(config);
                        }
                        mega_agent_one::Output::Occlusion(occlusion::Output::Estimate(output)) => {
                            occlusion = Some(Ok(output));
                            progress += OCCLUSION_PROGRESS;
                        }
                        mega_agent_one::Output::Occlusion(occlusion::Output::Error(error)) => {
                            occlusion = Some(Err(error));
                        }
                        mega_agent_one::Output::Iris(iris::Output::Estimate(
                            iris::EstimateOutput {
                                iris_code_shares,
                                mask_code_shares,
                                iris_code,
                                mask_code,
                                iris_code_version,
                                metadata,
                                normalized_image,
                                normalized_image_resized,
                            },
                        )) => {
                            iris_left = Some(EyePipeline {
                                iris_code_shares,
                                mask_code_shares,
                                iris_code,
                                mask_code,
                                iris_code_version,
                                metadata,
                                iris_normalized_image: normalized_image,
                                iris_normalized_image_resized: normalized_image_resized,
                            });

                            self.set_timeout();
                            progress += IRIS_ESTIMATE_PROGRESS;
                        }
                        mega_agent_one::Output::Iris(iris::Output::Version(version)) => {
                            iris_version = Some(version);
                        }
                        mega_agent_one::Output::Iris(
                            iris::Output::Error(error),
                            // If IIP or Iris fail, there is not much we can do.
                        ) => return Err(Error::Iris(error))?,
                        mega_agent_one::Output::IRNet(ir_net::Output::Version(version)) => {
                            ir_net_version = Some(version);
                        }
                        o @ mega_agent_one::Output::IRNet(_) => {
                            unreachable!("{o:?} is not part of biometric pipeline!")
                        }
                    }
                }
```

**File:** agentwire/src/port.rs (L743-760)
```rust
fn serialize_message<T>(
    buf: &mut [u8],
    scratch: &mut Option<FallbackScratch<HeapScratch<SCRATCH_SIZE>, AllocScratch>>,
    value: &T,
) where
    T: Archive + for<'a> Serialize<SharedSerializer<'a>> + Debug,
{
    let mut serializer = CompositeSerializer::new(
        BufferSerializer::new(&mut buf[mem::size_of::<usize>()..]),
        scratch.take().unwrap(),
        SharedSerializeMap::new(), // reuse of this map doesn't work
    );
    serializer.serialize_value(value).expect("failed to serialize an IPC message");
    let size = serializer.pos();
    let (_, c, _) = serializer.into_components();
    buf[..mem::size_of::<usize>()].copy_from_slice(&size.to_ne_bytes());
    *scratch = Some(c);
}
```
