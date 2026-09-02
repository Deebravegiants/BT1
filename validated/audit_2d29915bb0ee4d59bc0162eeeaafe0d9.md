This confirms the vulnerability: `ShopifyAPI::Webhooks::Request#hmac` is computed and verified solely over `to_signable_string` (the raw body) via `HmacValidator.validate_signature`, while `shop` (from `x-shopify-shop-domain`/`shopify-shop-domain` header) is never included in the HMAC-signed content. `Registry.process` only checks `Utils::HmacValidator.validate(request)` — which validates body integrity — then blindly forwards `request.shop` into `WebhookMetadata.shop`, which host apps use to select the tenant/shop record (as documented in `docs/usage/webhooks.md` example: `perform_later(topic: data.topic, shop_domain: data.shop, ...)`).

### Title
Webhook shop-domain header is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw request body via HMAC, but the `shop` (tenant identity) is read from an unauthenticated header. Since Shopify's HMAC signature only covers the body, an attacker who possesses one valid `(raw_body, hmac)` pair for any topic (e.g., from their own installed shop) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain`/`shopify-shop-domain` header. The signature remains valid because the header is not part of the signed content, and the host app receives `WebhookMetadata.shop` pointing at a victim shop while processing attacker-controlled body content.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is parsed straight from a header with no relation to the signed bytes: [2](#0-1) 

`HmacValidator.validate_signature` computes the signature over `verifiable_query.to_signable_string` only — i.e., the body — and compares it against the `hmac` header: [3](#0-2) 

`Registry.process` gates entirely on this body-only HMAC check, then forwards the unauthenticated `request.shop` directly into `WebhookMetadata`, which is the identity binding used by the host application: [4](#0-3) 

`WebhookMetadata.shop` is the field host apps are documented to use as the tenant key (`shop_domain: data.shop`) for dispatching work: [5](#0-4) [6](#0-5) 

The identity binding broken is: `shop header used for tenant dispatch` ≠ `shop bytes actually covered by the verified HMAC` (the HMAC covers zero bytes of the shop identity — only the body). Any entity capable of obtaining one legitimately-signed `(body, hmac)` pair (trivially available to any developer/merchant who installs the app on their own store and receives a real webhook) can resend that pair with a forged shop header to impersonate any other tenant to the app's webhook consumer, since this gem performs no header-to-signature binding check.

### Impact Explanation
This is a cross-tenant identity confusion: the gem's own webhook validation primitive (`HmacValidator` + `Registry.process`) certifies "this body is genuine Shopify content" but is silently relied upon by consuming apps (per this gem's own documented usage pattern) to also certify "this body belongs to shop X." Because the gem exposes `request.shop` as if it were an authenticated field alongside a validated HMAC, apps built per the documented pattern will attribute attacker-controlled bodies to an arbitrary victim shop domain, enabling data injection/corruption into another tenant's records, cache poisoning, or triggering shop-specific business logic (e.g., order/webhook processing) under a spoofed tenant — a cross-tenant boundary violation.

### Likelihood Explanation
Likelihood is significant: the attacker needs only one legitimate webhook (topic/body/hmac triple) from Shopify to their own shop's app installation — something any developer testing the app already receives — and then replays it to the app's public webhook endpoint with an arbitrary `x-shopify-shop-domain` header. No secret, token, or privileged access is required beyond normal use of the app as a merchant on one's own store.

### Recommendation
Include the shop domain (and ideally topic/api-version/webhook-id) as part of the signable content that is checked against the HMAC, or otherwise explicitly document that `Request#shop` is unauthenticated and must not be used as a trust boundary. Since Shopify computes the HMAC only over the raw body server-side, this gem cannot retroactively bind the header without an out-of-band verification mechanism — the safest fix is to require host apps to independently verify the `shop` against a known/registered shop list (e.g., cross-reference against sessions already persisted for that shop from OAuth) before trusting `WebhookMetadata.shop`, and to add an explicit warning to `docs/usage/webhooks.md` that the `shop` field is unauthenticated by HMAC.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g., `orders/create`) to capture a legitimate `(raw_body, x-shopify-hmac-sha256)` pair delivered by Shopify.
2. Replay an HTTP POST to the app's webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256` header, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds the request; `Utils::HmacValidator.validate` succeeds because it only recomputes HMAC over `raw_body`, per [7](#0-6)  and [1](#0-0) .
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: attacker_controlled_body, ...)`, per [8](#0-7) , causing the host app to process attacker data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
