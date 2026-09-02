### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop-identity spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body [1](#0-0) . The `shop` and `topic` values used to route and label the webhook are read directly from HTTP headers that are excluded from the signed payload [2](#0-1) . This is the same bug class as CVE-2022-27778: an operation (attributing/handling data for `shop`) is performed based on a field (`shop-domain` header) that is not bound by the integrity check (the HMAC), so the two "identities" — the shop the HMAC actually authenticates (none) vs. the shop the request claims and the library trusts — can diverge.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: `Digest.hexencode(...)` is computed over the raw body alone [3](#0-2) . `Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over that same `to_signable_string` value and compares it to the `hmac` field via `OpenSSL.secure_compare` [4](#0-3) . Neither `shop`, `topic`, `webhook_id`, nor `api_version` — all read straight from headers via `shopify_header` [5](#0-4)  — participate in the signature.

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching to the registered handler with `shop: request.shop` taken verbatim from the header [1](#0-0) . The gem's own documentation tells integrators that `Registry.process` "will verify the request did indeed come from Shopify," implying the whole request (including shop attribution) is authenticated [6](#0-5) , and that `data.shop` is "The shop domain of the webhook" [7](#0-6)  — i.e. an authenticated attribute a handler is expected to trust for tenant routing.

Because `Context.api_secret_key` is a single shared app secret used for every shop that installs the app (not a per-shop secret), any shop that has installed the app can receive a legitimate `(raw_body, hmac)` pair signed with that shared secret. That pair remains valid under `HmacValidator.validate` regardless of which `shop-domain` header accompanies it, since the header is not part of `to_signable_string`. An attacker who controls one installed shop can therefore take their own valid `(raw_body, hmac)` pair and resubmit it to the app's webhook endpoint with the `shop-domain` header (and/or `topic`/`webhook_id`) changed to point at a different, victim shop.

**Binding broken (equality that should hold but doesn't):**
`shop authenticated by HMAC` == `shop attributed to the processed webhook (request.shop)`

Before the attacker's replay: both sides equal the legitimate shop that received the real webhook.
After the attacker crafts the replayed request: the HMAC still validates (it only ever authenticated the body, not the shop), but `request.shop` is now the attacker-chosen value — the two sides diverge while `HmacValidator.validate` still returns `true`.

### Impact Explanation
This breaks a shop/tenant identity binding without needing the app's `client_secret`, an access token, or any privileged credential — only participation as one (unprivileged) installed shop of a multi-tenant app is required. Handlers that key persistence, authorization, or side effects off `WebhookMetadata#shop` (as the documentation instructs them to do) can be made to act as if data belongs to a different shop, resulting in cross-tenant data confusion/access — one of the explicitly in-scope Critical impacts (cross-tenant access).

### Likelihood Explanation
Any actor able to install the target app on a shop they control (a normal, unprivileged flow for public apps) can capture one legitimate webhook body+HMAC pair with off-the-shelf tools, then replay it with a modified `shop-domain` (and/or `topic`/`webhook_id`) header against the same publicly reachable webhook endpoint. No cryptographic secret needs to be recovered because the header fields being spoofed were never covered by the signature in the first place.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed material verified against the HMAC, or otherwise cryptographically bind them to the payload (e.g., require the receiving app to independently confirm the shop owns/expects that webhook, such as checking it against a known set of shops with an active registration for that topic) before dispatching to handlers. At minimum, update the documentation to explicitly warn that `data.shop`/`data.topic` are unauthenticated header values and must not be trusted for tenant-sensitive decisions without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, causing Shopify to send a legitimate webhook to the app's shared endpoint with a real `x-shopify-hmac-sha256` computed over the raw body using the app's shared `api_secret_key`.
2. Attacker captures the raw body `B` and its valid signature `H`.
3. Attacker crafts a new HTTP request to the same app webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or a different `x-shopify-topic`).
4. `ShopifyAPI::Webhooks::Request.new` accepts the request (only requires the three headers to be present) [8](#0-7) .
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and finds it matches `H`, so validation succeeds [9](#0-8) .
6. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to process attacker-controlled data attributed to the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** docs/usage/webhooks.md (L14-14)
```markdown
- `shop`, `String` - The shop domain of the webhook
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
