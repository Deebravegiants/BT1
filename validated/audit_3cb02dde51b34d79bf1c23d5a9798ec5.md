### Title
Webhook `shop`, `topic`, and `webhook_id` headers are trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then unconditionally trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from HTTP headers to build the `WebhookMetadata` handed to the app's handler. Those header values are not part of the signed material, so the identity binding "HMAC-authenticated bytes == the shop this payload is attributed to" does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts `shop`, `topic`, `api_version`, and `webhook_id` directly from request headers: [1](#0-0) 

But `to_signable_string`, which is the only input to the HMAC check, returns just the raw body: [2](#0-1) 

`Utils::HmacValidator.validate` computes/compares the HMAC over that signable string only: [3](#0-2) 

`Registry.process` uses this HMAC check as the sole authentication gate, then immediately trusts the header-derived `request.shop`/`request.topic`/`request.webhook_id` to construct the metadata passed to the handler: [4](#0-3) 

The identity binding that should hold is:
`hmac_valid(secret, bytes) == true` should imply `bytes was produced by Shopify specifically for shop == request.shop`.

In reality, the binding only proves `bytes was produced by Shopify using this app's secret for *some* topic/shop combination that once existed`. The `shop`, `topic`, and `webhook_id` header values are attacker-controllable independently of the signed body, since only the raw body bytes feed the HMAC.

### Impact Explanation
Any unprivileged user who can trigger a legitimately signed webhook for one tenant (e.g., install the app on their own free development store and cause any webhook event) obtains a `(raw_body, hmac)` pair that is valid under the app's `api_secret_key`. Because `shop` (and `topic`/`webhook_id`) are not covered by the HMAC, that same `raw_body`/`hmac` pair can be replayed to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header pointing at a victim shop. `Registry.process` will pass HMAC validation and hand the handler a `WebhookMetadata` claiming the payload came from the victim shop. If the host application uses `WebhookMetadata#shop` (as documented/intended) to look up or mutate per-merchant state, this allows cross-tenant data injection/confusion — an attacker-controlled payload is processed under another merchant's identity.

### Likelihood Explanation
Likelihood is bounded by whether the host application trusts `WebhookMetadata#shop` as the sole tenant key without independently cross-checking it (e.g., against a shop known to have an active webhook registration/session) — which is exactly the pattern this library's docs and API surface encourage (`WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`). No credentials, tokens, or privileged access are required by the attacker; only the ability to receive one legitimately signed webhook from their own install and to POST HTTP requests to the target app's public webhook endpoint.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or a canonical hash of the full header set) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the body before trusting them in `WebhookMetadata`. At minimum, document prominently that `request.shop`/`request.topic` are unauthenticated header values and must be cross-checked by the host application against known/registered shops before being used as a tenant key.

### Proof of Concept
1. Install the app on an attacker-controlled development store; trigger any webhook event to receive a genuine `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's real `api_secret_key`.
2. Replay an HTTP POST to the target app's webhook endpoint using the same `raw_body` and `x-shopify-hmac-sha256` value, but set `x-shopify-shop-domain` to a victim shop's domain (and optionally change `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks the (unchanged) body against the (unchanged) HMAC.
4. `ShopifyAPI::Webhooks::Registry.process` builds `WebhookMetadata` with `shop` set to the victim's domain and invokes the registered handler, which processes attacker-supplied data as if it originated from the victim shop.

### Citations

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
