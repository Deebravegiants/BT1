This confirms the asymmetry: OAuth's `AuthQuery#to_signable_string` explicitly binds `shop` (along with `code`, `host`, `state`, `timestamp`) into the signed string, while `Webhooks::Request#to_signable_string` signs only the raw body and excludes `shop`, `topic`, `webhook-id`, and `api-version` entirely.### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, and `Utils::HmacValidator.validate` verifies the HMAC exclusively against that body. The `shop`, `topic`, `webhook-id`, and `api-version` values, all pulled from unauthenticated HTTP headers, are never part of the signed material, yet `shop` is exactly the field the registry hands to the app's handler to decide which tenant a webhook event belongs to.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
returning only `@raw_body`. The `shop` accessor is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [3](#0-2) 

`Webhooks::Registry.process` validates only that body-only HMAC, then constructs the metadata handed to the app's handler using the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` header values: [4](#0-3) 

This is the exact scenario in the rules ("a field acted on but not covered by the HMAC"): the identity binding that should hold is `shop authenticated by HMAC == shop consumed by the handler`, but the gem breaks this equality — `shop` is consumed by the handler while never being part of the signed bytes.

Contrast this with `Auth::Oauth::AuthQuery#to_signable_string`, which explicitly folds `shop` into the signed parameters: [5](#0-4) 
showing that the gem's own OAuth code treats `shop` as security-relevant and binds it, while the webhook path does not.

### Impact Explanation
The app's `api_secret_key` (client secret) is the same for every shop that installs a multi-tenant app. Because the webhook HMAC covers only the JSON body — never `shop-domain` — a valid `(body, hmac)` pair produced for one tenant is equally valid for any other tenant's shop-domain header, since the byte string being HMAC'd is identical. An attacker who can obtain one legitimate `(body, hmac)` pair (e.g., by installing the app themselves and observing/relaying a webhook delivered to their own endpoint) can replay that exact body+HMAC to the shared webhook endpoint while substituting a victim's `shop-domain` header. `HmacValidator.validate` still succeeds (rule matched: same body → same HMAC), and `Registry.process` forwards the attacker-chosen `shop` value straight into `WebhookMetadata`/handler logic. Depending on which topic's `(body, hmac)` was captured (e.g. `app/uninstalled`, `shop/redact`, `customers/redact`), the app can be tricked into performing tenant-scoped destructive or state-changing actions (data deletion, resetting installation state, disabling a subscription, etc.) against a shop the attacker does not control — a cross-tenant access/actions vulnerability, which is a Critical-class impact per the rules.

### Likelihood Explanation
Exploitation requires: (1) the attacker to be an app installer/tenant themselves (to obtain a valid `(body, hmac)` sample for the shared `api_secret_key`), and (2) the target app to key tenant-scoped side effects off `data.shop` from the webhook handler without any additional shop-existence/entitlement cross-check. This does not require the `api_secret_key`, an access token, or TLS interception — it only requires normal use of the app as an unprivileged merchant/tenant, which matches the required threat model. Likelihood is moderate: it depends on host applications following the documented `WebhookMetadata#shop` field for tenant dispatch (a normal, encouraged usage pattern of this gem, not a documented misuse), and the exact severity depends on which topics the app is subscribed to.

### Recommendation
Include the identity-relevant headers (`shop-domain` at minimum, ideally `topic` and `webhook-id` as well) in the signed material that `to_signable_string` returns for `Webhooks::Request`, mirroring how `Auth::Oauth::AuthQuery` binds `shop` into its signable string. Since Shopify's actual webhook HMAC is computed by Shopify only over the raw body (this is a real platform constraint, not purely a gem defect), the gem should at least document this clearly and/or provide a way for consuming apps to assert an expected shop domain, since currently nothing in the gem itself prevents the described replay across tenants sharing one `api_secret_key`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, a legitimate tenant.
2. Shopify delivers a genuine webhook (e.g., `app/uninstalled`) to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — note `H` does not depend on the `shop-domain` header at all, per `Request#to_signable_string` / `HmacValidator.validate_signature` (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
3. Attacker (having intercepted or triggered this delivery to their own endpoint/tunnel) replays the identical body `B` and HMAC header `H` to the same app endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(api_secret_key, B)`, which still equals `H`, so validation passes (`lib/shopify_api/webhooks/registry.rb:190`).
5. `Registry.process` invokes the handler with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to perform the topic's associated tenant action against the victim shop's record instead of the attacker's own.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
