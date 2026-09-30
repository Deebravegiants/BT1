# [?] Merge pull request #4449 from joostjager/fix-fuzz-panic

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2026-03-20
Source: https://github.com/lightningdevkit/rust-lightning/commit/4baa2f396d1e6224621449bfc882d6bb2435e471
Type: security-commit

## Details
Merge pull request #4449 from joostjager/fix-fuzz-panic

fuzz: use process::exit panic hook in stdin_fuzz to avoid macOS hang

## Patch
### fuzz/src/bin/base32_target.rs
```diff
@@ -57,6 +57,18 @@ fuzz_target!(|data: &[u8]| {
 fn main() {
 	use std::io::Read;
 
+	// On macOS, panic=abort causes the process to send SIGABRT which can leave it
+	// stuck in an uninterruptible state due to the ReportCrash daemon. Using
+	// process::exit in a panic hook avoids this by terminating cleanly.
+	#[cfg(target_os = "macos")]
+	std::panic::set_hook(Box::new(|panic_info| {
+		use std::io::Write;
+		let _ = std::io::stdout().flush();
+		eprintln!("{}\n{}", panic_info, std::backtrace::Backtrace::force_capture());
+		let _ = std::io::stderr().flush();
+		std::process::exit(1);
+	}));
+
 	let mut data = Vec::with_capacity(8192);
 	std::io::stdin().read_to_end(&mut data).unwrap();
 	base32_test(&data, lightning_fuzz::utils::test_logger::Stdout {});
```

### fuzz/src/bin/bech32_parse_target.rs
```diff
@@ -57,6 +57,18 @@ fuzz_target!(|data: &[u8]| {
 fn main() {
 	use std::io::Read;
 
+	// On macOS, panic=abort causes the process to send SIGABRT which can leave it
+	// stuck in an uninterruptible state due to the ReportCrash daemon. Using
+	// process::exit in a panic hook avoids this by terminating cleanly.
+	#[cfg(target_os = "macos")]
+	std::panic::set_hook(Box::new(|panic_info| {
+		use std::io::Write;
+		let _ = std::io::stdout().flush();
+		eprintln!("{}\n{}", panic_info, std::backtrace::Backtrace::force_capture());
+		let _ = std::io::stderr().flush();
+		std::process::exit(1);
+	}));
+
 	let mut data = Vec::with_capacity(8192);
 	std::io::stdin().read_to_end(&mut data).unwrap();
 	bech32_parse_test(&data, lightning_fuzz::utils::test_logger::Stdout {});
```

### fuzz/src/bin/bolt11_deser_target.rs
```diff
@@ -57,6 +57,18 @@ fuzz_target!(|data: &[u8]| {
 fn main() {
 	use std::io::Read;
 
+	// On macOS, panic=abort causes the process to send SIGABRT which can leave it
+	// stuck in an uninterruptible state due to the ReportCrash daemon. Using
+	// process::exit in a panic hook avoids this by terminating cleanly.
+	#[cfg(target_os = "macos")]
+	std::panic::set_hook(Box::new(|panic_info| {
+		use std::io::Write;
+		let _ = std::io::stdout().flush();
+		eprintln!("{}\n{}", panic_info, std::backtrace::Backtrace::force_capture());
+		let _ = std::io::stderr().flush();
+		std::process::exit(1);
+	}));
+
 	let mut data = Vec::with_capacity(8192);
 	std::io::stdin().read_to_end(&mut data).unwrap();
 	bolt11_deser_test(&data, lightning_fuzz::utils::test_logger::Stdout {});
```

### fuzz/src/bin/chanmon_consistency_target.rs
```diff
@@ -57,6 +57,18 @@ fuzz_target!(|data: &[u8]| {
 fn main() {
 	use std::io::Read;
 
+	// On macOS, panic=abort causes the process to send SIGABRT which can leave it
+	// stuck in an uninterruptible state due to the ReportCrash daemon. Using
+	// process::exit in a panic hook avoids this by terminating cleanly.
+	#[cfg(target_os = "macos")]
+	std::panic::set_hook(Box::new(|panic_info| {
+		use std::io::Write;
+		let _ = std::io::stdout().flush();
+		eprintln!("{}\n{}", panic_info, std::backtrace::Backtrace::force_capture());
+		let _ = std::io::stderr().flush();
+		std::process::exit(1);
+	}));
+
 	let mut data = Vec::with_capacity(8192);
 	std::io::stdin().read_to_end(&mut data).unwrap();
 	chanmon_consistency_test(&data, lightning_fuzz::utils::test_logger::Stdout {});
```

### fuzz/src/bin/chanmon_deser_target.rs
```diff
@@ -57,6 +57,18 @@ fuzz_target!(|data: &[u8]| {
 fn main() {
 	use std::io::Read;
 
+	// On macOS, panic=abort causes the process to send SIGABRT which can leave it
+	// stuck in an uninterruptible state due to the ReportCrash daemon. Using
+	// process::exit in a panic hook avoids this by terminating cleanly.
+	#[cfg(target_os = "macos")]
+	std::panic::set_hook(Box::new(|panic_info| {
+		use std::io::Write;
+		let _ = std::io::stdout().flush();
+		eprintln!("{}\n{}", panic_info, std::backtrace::Backtrace::force_capture());
+		let _ = std::io::stderr().flush();
+		std::process::exit(1);
+	}));
+
 	let mut data = Vec::with_capacity(8192);
 	std::io::stdin().read_to_end(&mut data).unwrap();
 	chanmon_deser_test(&data, lightning_fuzz::utils::test_logger::Stdout {});
```

### fuzz/src/bin/feature_flags_target.rs
```diff
@@ -57,6 +57,18 @@ fuzz_target!(|data: &[u8]| {
 fn main() {
 	use std::io::Read;
 
+	// On macOS, panic=abort causes the process to send SIGABRT which can leave it
+	// stuck in an uninterruptible state due to the ReportCrash daemon. Using
+	// process::exit in a panic hook avoids this by terminating cleanly.
+	#[cfg(target_os = "macos")]
+	std::panic::set_hook(Box::new(|panic_info| {
+		use std::io::Write;
+		let _ = std::io::stdout().flush();
+		eprintln!("{}\n{}", panic_info, std::backtrace::Backtrace::force_capture());
+		let _ = std::io::stderr().flush();
+		std::process::exit(1);
+	}));
+
 	let mut data = Vec::with_capacity(8192);
 	std::io::stdin().read_to_end(&mut data).unwrap();
 	feature_flags_test(&data, lightning_fuzz::utils::test_logger::Stdout {});
```

### fuzz/src/bin/fromstr_to_netaddress_target.rs
```diff
@@ -57,6 +57,18 @@ fuzz_target!(|data: &[u8]| {
 fn main() {
 	use std::io::Read;
 
+	// On macOS, panic=abort causes the process to send SIGABRT which can leave it
+	// stuck in an uninterruptible state due to the ReportCrash daemon. Using
+	// process::exit in a panic hook avoids this by terminating cleanly.
+	#[cfg(target_os = "macos")]
+	std::panic::set_hook(Box::new(|panic_info| {
+		use std::io::Write;
+		let _ = std::io::stdout().flush();
+		eprintln!("{}\n{}", panic_info, std::backtrace::Backtrace::force_capture());
+		let _ = std::io::stderr().flush();
+		std::process::exit(1);
+	}));
+
 	let mut data = Vec::with_capacity(8192);
 	std::io::stdin().read_to_end(&mut data).unwrap();
 	fromstr_to_netaddress_test(&data, lightning_fuzz::utils::test_logger::Stdout {});
```

### fuzz/src/bin/fs_store_target.rs
```diff
@@ -57,6 +57,18 @@ fuzz_target!(|data: &[u8]| {
 fn main() {
 	use std::io::Read;
 
+	// On macOS, panic=abort causes the process to send SIGABRT which can leave it
+	// stuck in an uninterruptible state due to the ReportCrash daemon. Using
+	// process::exit in a panic hook avoids this by terminating cleanly.
+	#[cfg(target_os = "macos")]
+	std::panic::set_hook(Box::new(|panic_info| {
+		use std::io::Write;
+		let _ = std::io::stdout().flush();
+		eprintln!("{}\n{}", panic_info, std::backtrace::Backtrace::force_capture());
+		let _ = std::io::stderr().flush();
+		std::process::exit(1);
+	}));
+
 	let mut data = Vec::with_capacity(8192);
 	std::io::stdin().read_to_end(&mut data).unwrap();
 	fs_store_test(&data, lightning_fuzz::utils::test_logger::Stdout {});
```

### fuzz/src/bin/full_stack_target.rs
```diff
@@ -57,6 +57,18 @@ fuzz_target!(|data: &[u8]| {
 fn main() {
 	use std::io::Read;
 
+	// On macOS, panic=abort causes the process to send SIGABRT which can leave it
+	// stuck in an uninterruptible state due to the ReportCrash daemon. Using
+	// process::exit in a panic hook avoids this by terminating cleanly.
+	#[cfg(target_os = "macos")]
+	std::panic::set_hook(Box::new(|panic_info| {
+		use std::io::Write;
+		let _ = std::io::stdout().flush();
+		eprintln!("{}\n{}", panic_info, std::backtrace::Backtrace::force_capture());
+		let _ = std::io::stderr().flush();
+		std::process::exit(1);
+	}));
+
 	let mut data = Vec::with_capacity(8192);
 	std::io::stdin().read_to_end(&mut data).unwrap();
 	full_stack_test(&data, lightning_fuzz::utils::test_logger::Stdout {});
```

### fuzz/src/bin/indexedmap_target.rs
```diff
@@ -57,6 +57,18 @@ fuzz_target!(|data: &[u8]| {
 fn main() {
 	use std::io::Read;
 
+	// On macOS, panic=abort causes the process to send SIGABRT which can leave it
+	// stuck in an uninterruptible state due to the ReportCrash daemon. Using
+	// process::exit in a panic hook avoids this by terminating cleanly.
+	#[cfg(target_os = "macos")]
+	std::panic::set_hook(Box::new(|panic_info| {
+		use std::io::Write;
+		let _ = std::io::stdout().flush();
+		eprintln!("{}\n{}", panic_info, std::backtrace::Backtrace::force_capture());
+		let _ = std::io::stderr().flush();
+		std::process::exit(1);
+	}));
+
 	let mut data = Vec::with_capacity(8192);
 	std::io::stdin().read_to_end(&mut data).unwrap();
 	indexedmap_test(&data, lightning_fuzz::utils::test_logger::Stdout {});
```

### fuzz/src/bin/invoice_deser_target.rs
```diff
@@ -57,6 +57,18 @@ fuzz_target!(|data: &[u8]| {
 fn main() {
 	use std::io::Read;
 
+	// On macOS, panic=abort causes the process to send SIGABRT which can leave it
+	// stuck in an uninterruptible state due to the ReportCrash daemon. Using
+	// process::exit in a panic hook avoids this by terminating cleanly.
+	#[cfg(target_os = "macos")]
+	std::panic::set_hook(Box::new(|panic_info| {
+		use std::io::Write;
+		let _ = std::io::stdout().flush();
+		eprintln!("{}\n{}", panic_info, std::backtrace::Backtrace::force_capture());
+		let _ = std::io::stderr().flush();
+		std::process::exit(1);
+	}));
+
 	let mut data = Vec::with_capacity(8192);
 	std::io::stdin().read_to_end(&mut data).unwrap();
 	invoice_deser_test(&data, lightning_fuzz::utils::test_logger::Stdout {});
```

### fuzz/src/bin/invoice_request_deser_target.rs
```diff
@@ -57,6 +57,18 @@ fuzz_target!(|data: &[u8]| {
 fn main() {
 	use std::io::Read;
 
+	// On macOS, panic=abort causes the process to send SIGABRT which can leave it
+	// stuck in an uninterruptible state due to the ReportCrash daemon. Using
+	// process::exit in a panic hook avoids this by terminating cleanly.
+	#[cfg(target_os = "macos")]
+	std::panic::set_hook(Box::new(|panic_info| {
+		use std::io::Write;
+		let _ = std::io::stdout().flush();
+		eprintln!("{}\n{}", panic_info, std::backtrace::Backtrace::force_capture());
+		let _ = std::io::stderr().flush();
+		std::process::exit(1);
+	}));
+
 	let mut data = Vec::with_capacity(8192);
 	std::io::stdin().read_to_end(&mut data).unwrap();
 	invoice_request_deser_test(&data, lightning_fuzz::utils::test_logger::Stdout {});
```
