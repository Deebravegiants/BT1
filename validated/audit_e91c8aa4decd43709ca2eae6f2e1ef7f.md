### Title
Webhook `shop` identity is taken from an HTTP header that is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `x-shopify-shop-domain` HTTP header, but the HMAC validation performed by `ShopifyAPI::Utils::HmacValidator` only signs the raw request body, never the shop header. This breaks the identity binding `HMAC(secret, signed_bytes) == HMAC(secret, bytes_the_app_acts_on)` and lets any party that can produce one genuine, HMAC-valid webhook body (e.g. a merchant who has installed the app on their own store and receives real webhooks for it) relabel that payload as coming from a different shop.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via: [1](#0-0) 
```
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
```
`HmacValidator.validate` computes and compares the HMAC only over `to_signable_string`, which for webhook `Request` objects is defined as the raw HTTP body: [2](#0-1) 

Meanwhile, `request.shop` — the value passed to the handler as the tenant identifier — is read directly out of the unauthenticated `x-shopify-shop-domain` header, entirely independent of the signed bytes: [3](#0-2) [4](#0-3) 

The equality that should hold but does not: `shop_bound_by_HMAC == shop_header_value`. The HMAC secret used for webhooks is the app-level `api_secret_key` shared across every shop that installs the app (not a per-shop secret), so any merchant who has legitimately installed the app can capture a real, validly-signed webhook body sent to their own store, then resend that exact body to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. `HmacValidator.validate` still passes because it never inspects the shop header, and `Registry.process` forwards the attacker-chosen shop into `WebhookMetadata`, which the host application's handler will treat as authentic.

### Impact Explanation
This is a cross-tenant identity-binding failure at the gem layer: the field that identifies which tenant a webhook applies to is never bound to the cryptographic signature that is supposed to authenticate the message. Any handler built on top of this gem's webhook processing (session revocation on `app/uninstalled`, data sync webhooks, etc.) can be tricked into acting on data attributed to a shop the attacker does not own, using a signature that was legitimately produced for the attacker's own shop. This satisfies the Critical "cross-tenant access" impact category, since the vulnerability is in the gem's own binding logic, not a misuse of a documented API by the host app.

### Likelihood Explanation
Exploitability only requires the attacker to be an ordinary, unprivileged merchant who has installed the app once (a normal, low-privilege condition, not a leaked secret or TLS interception). They receive genuine signed webhooks for their own shop as part of normal app usage and can replay the body with a forged shop header to the app's public webhook endpoint.

### Recommendation
Bind the tenant identity into the authenticated bytes before trusting it. At minimum, `HmacValidator`/`Request#to_signable_string` should incorporate the `x-shopify-shop-domain` value (and ideally topic/webhook-id) into the signed material it verifies, or the registry should independently confirm that the shop in the header matches a shop that Shopify's webhook delivery metadata is provably tied to (e.g. via a per-shop webhook secret) rather than trusting an arbitrary header value once only the body HMAC has been checked.

### Proof of Concept
1. App developer installs their own app to a shop they control (`attacker.myshopify.com`) and receives a real webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC_SHA256(api_secret_key, B)`.
2. Attacker resends `POST /webhooks` to the app's endpoint with the identical body `B` and header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds `request.shop == "victim.myshopify.com"` while `request.hmac`/`to_signable_string` are unaffected by that header.
4. `Utils::HmacValidator.validate(request)` recomputes `HMAC_SHA256(api_secret_key, B)`, which equals `H`, so validation succeeds.
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...))`, causing the host app to process attacker-supplied data as if it originated from the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L9-13)
```ruby

      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```
