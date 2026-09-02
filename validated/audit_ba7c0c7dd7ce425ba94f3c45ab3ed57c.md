This confirms the documented contract: `ShopifyAPI::Webhooks::Registry.process` is documented to "verify the request did indeed come from Shopify" (docs/usage/webhooks.md:125), and the `shop` field of `WebhookMetadata` is documented as "The shop domain of the webhook" (docs/usage/webhooks.md:14) — i.e., it's meant to be a trusted tenant identifier that host apps use directly (as shown in the doc's own example, `perform_later(topic: data.topic, shop_domain: data.shop, ...)`). But the HMAC computed in `HmacValidator` only signs `to_signable_string`, which for `Webhooks::Request` is just `@raw_body`, never including the `shop-domain` header.

### Title
Webhook shop-domain header is not covered by HMAC, allowing cross-tenant spoofing of webhook origin - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook using `Utils::HmacValidator.validate(request)`, which only verifies `request.to_signable_string` against `request.hmac`. For `Webhooks::Request`, `to_signable_string` returns solely the raw body [1](#0-0) , while the `shop` value used by the handler as the tenant identifier is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, completely outside the HMAC's coverage [2](#0-1) .

### Finding Description
The identity binding broken is: `HMAC-verified bytes (raw_body) == identity used for tenant routing (shop-domain header)`. Shopify signs webhooks with `HMAC-SHA256(client_secret, raw_body)` — the body only. This gem's `HmacValidator.validate_signature` recomputes the signature over `verifiable_query.to_signable_string`, which for `Webhooks::Request` is `@raw_body` [1](#0-0)  and [3](#0-2) . The `shop` accessor, however, is pulled straight from the `shop-domain` header without any cryptographic binding to that header value [2](#0-1) .

`Registry.process` uses this unauthenticated `request.shop` to build the `WebhookMetadata` passed to the app's handler, which the docs explicitly say represents "the shop domain of the webhook" and instruct app authors to use directly for tenant-scoped work (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [4](#0-3)  and docs/usage/webhooks.md lines 12–26 above. Because the app's `client_secret` is a single shared value across every shop that installs the app, any webhook body signed with a valid HMAC for one shop is a valid HMAC for that same body sent under a different shop's identity — the signature carries no shop binding at all. An attacker who controls an unprivileged shop that has installed the app (or otherwise obtains one genuine, validly-signed webhook payload — e.g. topics whose payload is constant such as `{}` for `app/uninstalled`, or payloads that don't embed a shop-specific token) can replay that exact `raw_body` + `hmac` pair to the app's webhook endpoint while substituting the `shop-domain` (or `x-shopify-shop-domain`) header with a victim shop's domain. `Registry.process` will pass HMAC validation and dispatch the handler believing the event originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is documented to enforce ("verify the request did indeed come from Shopify" for a specific shop). A host application that keys shop-scoped side effects (queued jobs, data updates, deduplication, redaction/GDPR topics like `customers/redact` or `shop/redact`) off `data.shop` as instructed by this gem's own documentation can be made to apply attacker-influenced or replayed events under another tenant's identity, i.e., cross-tenant contamination stemming purely from this gem's identity-binding gap, not from the host app deviating from documented usage.

### Likelihood Explanation
Moderate-to-high: no access token, `client_secret`, or privileged account is required — the reporter only needs to be a legitimate merchant/installer of the app (unprivileged internet user relative to other tenants) to obtain one real, validly-signed webhook body/HMAC pair, then replay it with a spoofed shop header at the app's public webhook endpoint.

### Recommendation
Bind the shop domain (and ideally topic/webhook-id) into the HMAC-covered signable string, or otherwise independently authenticate the shop identity for the given HMAC (e.g., require the app to look up an installed session for the claimed shop and reject if no matching, currently-active installation exists), and document that `data.shop` must not be trusted as authenticated on its own without further binding.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a genuine webhook, e.g. `app/uninstalled` with body `{}`, headers including a valid `X-Shopify-Hmac-Sha256` computed over `{}` with the app's shared `client_secret`, plus `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends the identical `raw_body` (`{}`) and identical `X-Shopify-Hmac-Sha256` value to the app's `/webhook` endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers [5](#0-4) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body's HMAC [6](#0-5) .
4. The handler is invoked with `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"` [7](#0-6) , even though the event never actually happened on that shop.

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
