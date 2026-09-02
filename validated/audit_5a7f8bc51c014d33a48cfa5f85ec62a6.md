### Title
Webhook `shop` tenant identifier is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the tenant-identifying `shop` (and `topic`/`webhook_id`/`api_version`) values are read from separate, unsigned HTTP headers. `Registry.process` accepts any request whose *body* HMAC matches, then forwards the unauthenticated `shop` header value straight to the app's webhook handler as trusted tenant metadata.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 

But `shop` (and `topic`, `api_version`, `webhook_id`) are pulled from separate HTTP headers that are never included in the signed string: [3](#0-2) 

`Registry.process` validates only the HMAC of the body and then dispatches the handler using the unauthenticated `shop` header as the tenant identity: [4](#0-3) 

The identity binding that should hold is: **bytes verified by HMAC == bytes used to determine the tenant (`shop`)**. Here, the HMAC only binds the body bytes; the `shop` header is parsed and trusted independently, exactly the "bytes verified versus bytes parsed" mismatch called out in the audit brief, and structurally analogous to the Perennial adiabatic-fee bug where the exposure adjustment was weighted by a value (position size) that wasn't the value actually owed (individual exposure) — here the trust decision (HMAC-valid) is made on one field (body) but applied to a different, uncorrelated field (shop header) that drives tenant-scoped business logic.

### Impact Explanation
Any unprivileged internet user who can obtain **one** valid `(body, hmac)` pair — e.g., by installing the app on their own shop and capturing a legitimate webhook delivery, since webhook endpoints are public HTTP URLs — can replay that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds because it never inspects the header, and `Registry.process` calls the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain. Any host application that uses this `shop` field to route data into per-tenant storage (the documented purpose of `WebhookMetadata#shop`) can be made to attribute attacker-controlled webhook payloads to a different merchant, i.e., cross-tenant data injection/confusion under an attacker-chosen tenant identity.

### Likelihood Explanation
Exploitation requires only a single legitimate webhook capture (trivial for an attacker who installs the app on a shop they control) and the ability to send an arbitrary HTTP POST with custom headers to the app's public webhook endpoint — no access to `api_secret_key`, access tokens, or any privileged credential is needed. Likelihood is high for any app that relies on `WebhookMetadata#shop` for tenant routing, which is the intended use of that field per the gem's own webhook handler API.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`/`api_version`) header values in the signable string used for HMAC computation, or independently authenticate the `shop` value (e.g., by validating it against the shop tied to the app installation/session that the webhook logically corresponds to) before passing it downstream in `WebhookMetadata`.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; capture a legitimate webhook POST, e.g., body `{"id":1}` with header `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Replay the identical body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request#hmac`/`#to_signable_string` only exposes/signs the body, so `Utils::HmacValidator.validate` returns `true`.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: <attacker body>, ...)`, as shown at `lib/shopify_api/webhooks/registry.rb:198-199`, causing the host app to process attacker data as if it originated from `victim-shop`.

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

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
