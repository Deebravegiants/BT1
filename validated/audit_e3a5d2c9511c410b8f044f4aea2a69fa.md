### Title
Webhook shop/topic identity spoofing via HMAC that only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content as the raw request body only [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read from separate, unsigned HTTP headers [2](#0-1) . `Utils::HmacValidator.validate` only checks that the received HMAC matches `to_signable_string` (the body) [3](#0-2) , so the tenant-identifying `shop` field is never bound to the signature that authenticates the request.

### Finding Description
`Registry.process` authenticates a webhook purely via `Utils::HmacValidator.validate(request)` and then trusts `request.shop`/`request.topic` to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) .

The HMAC secret (`Context.api_secret_key`, the app's client secret) is a single, shared value across every shop that installs the app — it is not per-tenant. Because the signed content is only the raw body [5](#0-4) , the same `(raw_body, hmac)` pair that Shopify computes and delivers for a webhook on shop A is a cryptographically valid signature for that exact byte sequence regardless of which `shop-domain` header accompanies it. A merchant who has installed the app on their own shop (an unprivileged, non-credentialed party from the app's perspective — they never see `api_secret_key`) can legitimately trigger a webhook (e.g. `orders/create`) for their own store, capture the resulting `(body, X-Shopify-Hmac-Sha256)` pair that Shopify sent, and replay it to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`) header to name a victim shop. `HmacValidator.validate` still succeeds because it only checks the body bytes, yet `Registry.process` and the resulting `WebhookMetadata` will assert the event came from the victim shop [4](#0-3) .

This is exactly the "field acted on but not covered by the HMAC" identity-binding break: the equality the app relies on is `shop_authenticated == shop_used_by_handler`, but the gem only guarantees `body_bytes_authenticated == body_bytes_used_by_handler`. `shop` and `topic` are asserted, not authenticated.

### Impact Explanation
Any host application that uses `WebhookMetadata#shop` (or `#topic`) to select which tenant's records to create/update/delete — the documented, intended use of this API — can be made to apply attacker-controlled webhook payload data to a different merchant's tenant/data, i.e. cross-tenant data injection/corruption. This matches the "Critical - cross-tenant access" impact bucket: an attacker who is a legitimate but unprivileged user of the app (their own shop install) can cause the library to authenticate the request and hand the app a spoofed tenant identity for a shop they do not control, entirely through the app's own public webhook endpoint using only their own shop's genuine webhook traffic.

### Likelihood Explanation
Likelihood is realistic but conditional: the attacker needs to be able to trigger at least one webhook delivery for a topic/body shape useful for cross-tenant impact (trivial for topics like `orders/create`, `customers/create`, `app/uninstalled`, etc., in their own store), and the target app must key its persistence/logic off `WebhookMetadata#shop` from this library without additional cross-checks (this is the standard, documented pattern in `docs/usage/webhooks.md`). No secret, access token, or privileged role is required — only ordinary use of a merchant's own store to obtain a validly-signed body/HMAC pair, then a forged HTTP header sent to the app's public webhook receiver.

### Recommendation
Include the `shop-domain` and `topic` headers (and ideally `webhook-id`/`api-version`) in the signed material verified against the HMAC, or otherwise cryptographically bind them (e.g. verify the shop domain against a value obtained from a trusted server-side store to app-installation mapping, not solely the header on the same request). At minimum, document loudly that `shop`/`topic` are unauthenticated header values and must not be trusted for tenant selection without an independent binding (e.g., cross-referencing against the shop associated with the webhook subscription ID via a authenticated Admin API call), and consider adding a library-level check that `request.shop` matches an expected/allow-listed shop before constructing `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged install).
2. Attacker performs an action that fires a webhook, e.g. creates an order, causing Shopify to POST to the app's webhook endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures `(B, H)` (e.g., via a proxy on their own request path, or by controlling the receiving webhook URL temporarily).
4. Attacker replays the exact same request to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (and/or a chosen `X-Shopify-Topic`), leaving `B` and `H` unchanged.
5. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...spoofed shop...})` builds successfully [6](#0-5) ; `Utils::HmacValidator.validate(request)` returns `true` because it recomputes `HMAC-SHA256(client_secret, B)` and compares to `H`, which still matches [3](#0-2) .
6. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)` [4](#0-3) , causing the host app to process attacker-supplied data under the victim shop's identity.

**Uncertainty note:** I could not locate the `WebhookMetadata` class definition itself in the indexed portion of the repository (only references in `registry.rb`, `webhook_handler.rb`, and docs were found), so I cannot confirm whether any additional field-level validation exists there; based on all reachable code (`Request`, `HmacValidator`, `Registry.process`), no such cross-check exists before the handler is invoked.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
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
