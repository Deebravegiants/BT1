[1](#0-0) [2](#0-1)

### Citations

**File:** src/plans/qr_scan/operator.rs (L35-38)
```rust
impl Schema for Data {
    fn ui() -> ui::QrScanSchema {
        ui::QrScanSchema::Operator
    }
```

**File:** src/plans/qr_scan/operator.rs (L40-61)
```rust
    fn try_parse(code: &str) -> Option<Self> {
        let normal = user::Data::try_parse(code)
            .filter(
                |d| if d.signup_extension() { d.signup_extension_config.is_some() } else { true },
            )
            .map(Data::Normal);
        if normal.is_some() {
            return normal;
        }
        if let Some(captures) = MAGIC_QR_CODE.captures(code) {
            return match captures
                .name("magic_action")
                .expect("magic_action group must be present")
                .as_str()
            {
                "reset_wifi_credentials" => Some(Data::MagicResetWifi),
                "reset_mirror_calibration" => Some(Data::MagicResetMirror),
                _ => None,
            };
        }
        None
    }
```
