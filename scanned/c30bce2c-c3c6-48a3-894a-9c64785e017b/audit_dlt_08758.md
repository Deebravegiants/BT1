# [?] vendor: update USB HID lib (fix macOS crash)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2017-08-21
Source: https://github.com/scroll-tech/go-ethereum/commit/3e14837c1c711f70a7d8373213f24b95e0bab3ca
Type: security-commit

## Details
vendor: update USB HID lib (fix macOS crash)

## Patch
### vendor/github.com/karalabe/hid/README.md
```diff
@@ -24,6 +24,12 @@ and go-gettable.
 Supported platforms at the moment are Linux, macOS and Windows (exclude constraints are also specified
 for Android and iOS to allow smoother vendoring into cross platform projects).
 
+## Cross-compiling
+
+Using `go get` the embedded C library is compiled into the binary format of your host OS. Cross compiling to a different platform or architecture entails disabling CGO by default in Go, causing device enumeration `hid.Enumerate()` to yield no results.
+
+To cross compile a functional version of this library, you'll need to enable CGO during cross compilation via `CGO_ENABLED=1` and you'll need to install and set a cross compilation enabled C toolkit via `CC=your-cross-gcc`.
+
 ## Acknowledgements
 
 Although the `hid` package is an implementation from scratch, it was heavily inspired by the existing
```

### vendor/github.com/karalabe/hid/appveyor.yml
```diff
@@ -29,3 +29,4 @@ install:
 
 build_script:
   - go install ./...
+  - go test -v ./...
```

### vendor/github.com/karalabe/hid/hid.go
```diff
@@ -2,7 +2,7 @@
 // Copyright (c) 2017 Péter Szilágyi. All rights reserved.
 //
 // This file is released under the 3-clause BSD license. Note however that Linux
-// support depends on libusb, released under GNU GPL 2.1 or later.
+// support depends on libusb, released under GNU LGPL 2.1 or later.
 
 // Package hid provides an interface for USB HID devices.
 package hid
```

### vendor/github.com/karalabe/hid/hid_disabled.go
```diff
@@ -2,7 +2,7 @@
 // Copyright (c) 2017 Péter Szilágyi. All rights reserved.
 //
 // This file is released under the 3-clause BSD license. Note however that Linux
-// support depends on libusb, released under GNU GPL 2.1 or later.
+// support depends on libusb, released under GNU LGPL 2.1 or later.
 
 // +build !linux,!darwin,!windows ios !cgo
 
```

### vendor/github.com/karalabe/hid/hid_enabled.go
```diff
@@ -2,7 +2,7 @@
 // Copyright (c) 2017 Péter Szilágyi. All rights reserved.
 //
 // This file is released under the 3-clause BSD license. Note however that Linux
-// support depends on libusb, released under GNU GPL 2.1 or later.
+// support depends on libusb, released under LGNU GPL 2.1 or later.
 
 // +build linux,cgo darwin,!ios,cgo windows,cgo
 
@@ -48,6 +48,15 @@ import (
 	"unsafe"
 )
 
+// enumerateLock is a mutex serializing access to USB device enumeration needed
+// by the macOS USB HID system calls, which require 2 consecutive method calls
+// for enumeration, causing crashes if called concurrently.
+//
+// For more details, see:
+//   https://developer.apple.com/documentation/iokit/1438371-iohidmanagersetdevicematching
+//   > "subsequent calls will cause the hid manager to release previously enumerated devices"
+var enumerateLock sync.Mutex
+
 func init() {
 	// Initialize the HIDAPI library
 	C.hid_init()
@@ -66,6 +75,9 @@ func Supported() bool {
 //  - If the product id is set to 0 then any product matches.
 //  - If the vendor and product id are both 0, all HID devices are returned.
 func Enumerate(vendorID uint16, productID uint16) []DeviceInfo {
+	enumerateLock.Lock()
+	defer enumerateLock.Unlock()
+
 	// Gather all device infos and ensure they are freed before returning
 	head := C.hid_enumerate(C.ushort(vendorID), C.ushort(productID))
 	if head == nil {
```

### vendor/vendor.json
```diff
@@ -183,10 +183,10 @@
 			"revisionTime": "2016-06-03T03:41:37Z"
 		},
 		{
-			"checksumSHA1": "sGdhjz2N/DpfiZrMnHSzl2H/YX8=",
+			"checksumSHA1": "UpjhOUZ1+0zNt+iIvdtECSHXmTs=",
 			"path": "github.com/karalabe/hid",
-			"revision": "875879887cf0560a993b57e04615944e1dd02a73",
-			"revisionTime": "2017-02-27T10:57:12Z",
+			"revision": "f00545f9f3748e591590be3732d913c77525b10f",
+			"revisionTime": "2017-08-21T10:38:37Z",
 			"tree": true
 		},
 		{
```
