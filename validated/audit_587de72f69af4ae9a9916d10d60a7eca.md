### Title
Webhook `shop` header is never authenticated or sanitized before being handed to host app handlers - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`Registry.process` validates the webhook HMAC over the raw body only, then builds `WebhookMetadata` using `request.shop`, which is read verbatim from the `X-Shopify-Shop-Domain`/`Shopify-Shop-Domain` header with no call to `Utils::ShopValidator.sanitize!` and no inclusion in the signed payload. Any party capable of producing a validly-HMAC'd body (e.g., an attacker who registers the webhook on their own development shop and forwards the callback to the target app with a modified shop header) can make the app's handler believe the payload belongs to an arbitrary shop string.

### Finding Description
The binding that should hold is: **authenticated shop (the shop cryptographically bound to the HMAC-verified payload) == `WebhookMetadata.shop` (the shop the host app acts on)**.

Tracing the code:
- `Webhooks::Request#shop` reads the header directly: `T.cast(shopify_header("shop-domain"), String)` [1](#0-0) .
- `Webhooks::Request#to_signable_string` returns only `@raw_body` [2](#0-1) , so the shop-domain header is never part of what's HMAC'd.
- `Utils::HmacValidator.validate` computes the signature purely over `verifiable_query.to_signable_string` (the body) and compares it against the received signature [3](#0-2) . It never inspects or constrains `request.shop`.
- `Registry.process` checks only `Utils::HmacValidator.validate(request)`, then immediately constructs `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` and dispatches it to the host app's handler [4](#0-3) . There is no call to `Utils::ShopValidator.sanitize!` anywhere in this path, unlike the OAuth flows (`token_exchange.rb`, `client_credentials.rb`, `refresh_token.rb`) which do call it [5](#0-4) .

Root cause: the `api_secret_key` used for HMAC validation is a single app-level (`client_secret`) value shared across all shops the app is installed on, not a per-shop secret. Because the shop-domain header is excluded from the signable string, a validly signed body/HMAC pair obtained from the attacker's own development shop remains valid regardless of what shop-domain header accompanies it when replayed to the target app. Since `request.shop` also bypasses `ShopValidator.sanitize!`, the value flowing into `WebhookMetadata.shop` is fully attacker-controlled, unauthenticated, and unvalidated as a real domain.

Exploit flow: attacker installs the app on their own dev shop, registers a webhook, receives a legitimate callback (body B, valid HMAC H for B). Attacker (running their own server, or directly) POSTs body B with header `X-Shopify-Hmac-Sha256: H` to the target app's public webhook endpoint but sets `X-Shopify-Shop-Domain` to any arbitrary string. `HmacValidator.validate` returns `true` (correctly verifying B was HMAC'd with the app secret) but this says nothing about the shop, and the host app's handler receives `WebhookMetadata.shop` equal to the attacker's chosen string.

No existing guard closes this: `HmacValidator.validate` only proves authenticity of the body payload, not the shop association; `ShopValidator.sanitize!` is never invoked in this path; there is no `state`/session comparison for webhooks (they're not OAuth); Sorbet's `T.cast`/`sig` only enforce that `shop` is a `String`, not that it is a trusted or self-consistent domain.

### Impact Explanation
A host app that (as documented) uses `WebhookMetadata.shop` to key merchant lookups will act on data intended for one shop/tenant while attributing it to an attacker-chosen shop identifier - a cross-tenant confusion/injection primitive. This is repeatable at will against any host app built on this gem, for every webhook topic the attacker can trigger on their own dev shop (e.g., `orders/create`, `app/uninstalled`), and the "victim" attribution string is entirely attacker-chosen (not limited to real shop domains), enabling injection into whatever data store/lookup keys off `shop`.

### Likelihood Explanation
Preconditions are minimal and fully within the attacker's stated capabilities: create a free development shop, install the target app, register a webhook, and capture one legitimately signed callback. No credentials, secrets, or privileged access are required. The attack costs a single HTTP request per forgery attempt and is trivially repeatable and automatable.

### Recommendation
Sanitize and authenticate `Webhooks::Request#shop` before it is trusted: call `Utils::ShopValidator.sanitize!(request.shop)` in `Registry.process` (or inside `Request#shop`) before constructing `WebhookMetadata`, and document/require that host apps additionally cross-check the incoming shop against a shop they know is currently installed (e.g., verify a session/record already exists for that shop) rather than trusting the header as an identity assertion on its own.

### Proof of Concept
minitest + Mocha/WebMock plan (no live shop):
1. Stub `Context.setup?` and `Context.api_secret_key` to a known test secret via `TestHelpers::Context` as done elsewhere in the suite.
2. Build `raw_body = '{"id":1}'` and compute `hmac = Base64.encode64(OpenSSL::HMAC.digest("sha256", secret, raw_body))`.
3. Construct `request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: {"x-shopify-hmac-sha256" => hmac, "x-shopify-topic" => "orders/create", "x-shopify-shop-domain" => "'; DROP TABLE shops; --", "x-shopify-api-version" => "2024-01", "x-shopify-webhook-id" => "1"})`.
4. Assert `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` even though `request.shop` fails `ShopifyAPI::Utils::ShopValidator.sanitize!(request.shop)` (assert it raises `Errors::InvalidShopError`).
5. Register a fake `WebhookHandler` via `Registry.add_registration`, mock its `handle` method with Mocha to capture the `data:` argument, call `Registry.process(request)`, and assert `data.shop == "'; DROP TABLE shops; --"` - proving `Registry.process` dispatches an unsanitized, attacker-controlled `shop` value despite successful HMAC validation.

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

**File:** lib/shopify_api/utils/shop_validator.rb (L50-64)
```ruby
        sig do
          params(
            shop: String,
            myshopify_domain: T.nilable(String),
          ).returns(String)
        end
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
        end
```
