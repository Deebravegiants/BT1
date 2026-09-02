This confirms the root cause: `ShopifyAPI::Webhooks::Registry.process` at [1](#0-0)  validates HMAC via `Utils::HmacValidator.validate(request)`, which computes the signature only over `request.to_signable_string` (the raw body) as defined in `ShopifyAPI::Webhooks::Request#to_signable_string` at [2](#0-1) . The `shop` value used to build `WebhookMetadata` (the tenant identity passed to the app's handler) is read from an HTTP header via `Request#shop` at [3](#0-2) , which is never part of the signed payload.

### Title
Webhook `shop` identity is read from an unauthenticated header while HMAC only signs the raw body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic if `Utils::HmacValidator.validate(request)` succeeds, but that validator only verifies the raw body bytes. The `shop` field that identifies which tenant the webhook belongs to is taken straight from the `X-Shopify-Shop-Domain` header and is passed unchanged into `WebhookMetadata`, which host apps use as the tenant key to route/persist webhook data. Because the header is outside the signed content, the equality the app relies on — "the shop whose secret validated this HMAC" == "the shop attributed to this webhook payload" — does not actually hold within this gem.

### Finding Description
- `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` ( [2](#0-1) ).
- `Utils::HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` header value ( [4](#0-3) ). Only the body is covered.
- `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled from headers via `shopify_header`, none of which feed into `to_signable_string` ( [5](#0-4)  and [6](#0-5) ).
- `Registry.process` only checks `Utils::HmacValidator.validate(request)`, then unconditionally forwards `request.shop` into `WebhookMetadata` given to the app's handler ( [1](#0-0) ).
- The documented handler contract explicitly tells apps to treat `data.shop` as "The shop domain of the webhook" and use it to key persistence/queuing (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`), per `docs/usage/webhooks.md` lines 12-30.

This is the same bug class as the reported analog: an event/attribute (`shop`) that identifies the affected tenant is produced from a source (`msg.sender`-equivalent = HTTP header) that isn't bound to the piece that was actually authenticated (the HMAC-signed body).

### Impact Explanation
Genuine Shopify webhook deliveries are signed per-app (all shops share the one `client_secret`), and the signature covers only the JSON body. If body content for two different shops' webhook events for the same topic/schema is identical or attacker-controllable/predictable (e.g., a webhook whose body doesn't embed the shop domain, or a replay of a previously captured, validly-signed body), an attacker who can influence or capture one valid `(body, hmac)` pair can present it with an arbitrary `X-Shopify-Shop-Domain` header and it will pass `HmacValidator.validate` and be attributed to that arbitrary shop's tenant in the app. Depending on how the host app uses `data.shop`, this enables cross-tenant data contamination (High) since it lets an outsider who obtains any one validly-HMAC'd webhook payload masquerade as a different tenant, without possessing that tenant's `access_token` or the app's `client_secret`.

### Likelihood Explanation
Exploitation requires the attacker to submit a request directly to the app's webhook endpoint with a modified `Shop-Domain` header while keeping a validly-signed body — feasible if body content is fixed/guessable per topic or if the attacker previously observed one valid webhook delivery (bodies/HMACs for webhooks are not treated as secret in transit, and endpoints are typically public POST routes with no other authentication per Shopify's model). No `api_secret_key`, access token, or privileged access is required, only network access to the app's already-public webhook callback URL.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed material, or independently verify that the header-provided `shop` matches an expected/registered shop for that HMAC before constructing `WebhookMetadata`. At minimum, document/require host apps to cross-check `data.shop` against their own known-installed shop list before trusting it, or extend `Utils::HmacValidator`/`Request#to_signable_string` so header-derived identity fields are covered by the signature comparison rather than trusted independently of it.

### Proof of Concept
1. Capture (or otherwise obtain) one legitimately Shopify-signed webhook POST for topic `orders/create`, e.g. body `body` and header `X-Shopify-Hmac-Sha256: hmac` computed by Shopify for `victim-shop.myshopify.com`.
2. Replay that exact `body`/`hmac` pair to the app's webhook endpoint but replace the header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` with `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` — unaffected by the header change — so validation succeeds ( [7](#0-6) ).
4. The handler receives `WebhookMetadata.new(..., shop: "attacker-shop.myshopify.com", body: <victim's data>, ...)` ( [8](#0-7) ), and any app that keys storage/queueing off `data.shop` as documented will attribute the victim's webhook payload to the attacker's shop record, or vice versa depending on which body/shop pairing is replayed.

### Citations

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
