I have confirmed the key finding: `lib/shopify_api/webhooks/request.rb`'s `to_signable_string` HMAC binding only covers `@raw_body`, while `shop` (the `shop-domain` header) is read separately by `shopify_header` and passed downstream unauthenticated relative to the HMAC.### Title
Webhook HMAC does not bind the `shop-domain` header, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only signs the raw request body, while `#shop` is read straight from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header. `Registry.process` validates the HMAC and then trusts `request.shop` as the tenant identity for the handler call, without that field ever being covered by the signature.

### Finding Description
`VerifiableQuery#to_signable_string` is the only thing `HmacValidator.validate` checks against the HMAC [1](#0-0) . For webhooks, that signable string is defined as just the raw body: [2](#0-1) 

`shop` is derived from a plain HTTP header (`shopify-shop-domain` / `x-shopify-shop-domain`) that is never included in `to_signable_string`, so it is completely outside the cryptographic binding. `Registry.process` validates the HMAC over the body, then immediately hands `request.shop` to the handler as the trusted tenant identifier: [3](#0-2) 

Crucially, `Context.api_secret_key` is the app's `client_secret` — a single, app-wide secret shared across **every** shop that has installed the app, not a per-shop secret. Any merchant who installs the app receives genuine webhook requests to their own callback endpoint, each carrying a valid `hmac-sha256` signature computed with that same shared secret over the body only.

The equality that should hold is:
`shop authenticated by signature == shop the app attributes the payload to`

Because `shop` is outside `to_signable_string`, this equality is never enforced: an attacker (any installed merchant, fully unprivileged relative to other tenants) can take a webhook they legitimately received for their own shop, keep the body and the (still-valid) `hmac-sha256` value, and replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop that also has the app installed. `HmacValidator.validate` still succeeds (same secret, same body, same signature), and `Registry.process` calls the handler with `data.shop` equal to the victim's domain while `data.body`/`data.webhook_id`/`data.api_version` are the attacker's own data.

### Impact Explanation
This is a cross-tenant confusion primitive: the app-level webhook processing pipeline can be made to attribute one shop's legitimately-signed payload to a different shop. Any downstream logic in the host app that keys business actions, session lookups, or data writes off `data.shop` from `WebhookMetadata` can be tricked into acting on/for the wrong tenant using attacker-controlled body content, purely because the identity field is unauthenticated. This is a High-impact cross-tenant issue with no need for TLS interception, access tokens, or the app's `client_secret` — the attacker already legitimately possesses a validly signed request for their own tenant.

### Likelihood Explanation
High. Any merchant that installs a public app receives real webhook traffic to the endpoint they control, so capturing a valid `(raw_body, hmac)` pair is trivial and requires no privileged access, secret theft, or network interception — only replaying their own webhook with one header value changed.

### Recommendation
Include the shop domain (and ideally topic/api-version/webhook-id) in the signable string used for webhook HMAC validation, or otherwise cryptographically bind the asserted `shop-domain` header to the signature (e.g., validate that the shop belongs to an app installation the app already tracks, in addition to HMAC validity) before dispatching to handlers in `Registry.process`.

### Proof of Concept
1. App merchant "attacker.myshopify.com" installs the target app and receives a legitimate webhook:
```
POST /callback/orders/create
x-shopify-topic: orders/create
x-shopify-hmac-sha256: <valid signature over body, computed with the app's shared client_secret>
x-shopify-shop-domain: attacker.myshopify.com
x-shopify-webhook-id: abc-123
Body: {"id": 1, "note": "attacker-controlled"}
```
2. Attacker resends the exact same body/HMAC to the same endpoint but swaps the header:
```
x-shopify-shop-domain: victim.myshopify.com
```
3. `ShopifyAPI::Webhooks::Registry.process` at `lib/shopify_api/webhooks/registry.rb:190` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `request.to_signable_string` (the raw body) against the shared secret — the modified `shop-domain` header is never checked.
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: {"id": 1, "note": "attacker-controlled"}, ...)`, i.e., attacker-controlled content attributed to `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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
        end
```
