### Title
Webhook `shop` (and `topic`) header not covered by HMAC allows tenant-spoofed webhook delivery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the HMAC to the raw body only, while `shop`, `topic`, and `webhook_id` are read straight from unauthenticated headers and forwarded to the app's handler as the trusted tenant identity. An attacker who legitimately controls one shop's installation of the app (and therefore receives genuinely-signed webhooks for that shop) can replay the same signed body while swapping the `shop-domain`/`topic` headers, and `Registry.process` will accept it as authentic and dispatch it as if it belonged to a different shop/topic.

### Finding Description
`HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string` using the app's `api_secret_key`: [1](#0-0) 

For webhooks, `to_signable_string` only returns `@raw_body`: [2](#0-1) 

But `shop`, `topic`, and `webhook_id` are pulled directly from HTTP headers, which are not part of the signed material at all: [3](#0-2) 

`Registry.process` validates only the HMAC, then unconditionally trusts `request.shop`/`request.topic` to select the handler and to attribute the payload to a shop: [4](#0-3) 

The binding that should hold is:
`shop authenticated by the HMAC == shop the handler is told owns this payload`

Because the signature only covers `@raw_body`, this equality is never enforced — the `shop` (and `topic`) value can be freely substituted by anyone who possesses one valid `(body, hmac)` pair for the app's shared `api_secret_key`, since every shop installing the same app shares that secret for webhook signing. Since the header value is never cross-checked against the body or against any known-shop registry, a webhook truthfully delivered for Shop A can be re-submitted with the header changed to Shop B, and the gem will report it as valid, `shop`-labeled data for Shop B.

### Impact Explanation
This is a cross-tenant identity-binding break: the HMAC only authenticates that "this body came from someone possessing the app's secret," not "this body belongs to shop X." An attacker who is a legitimate (even unprivileged) merchant installer of the target app can forge the tenant attribution of any of their own real webhook deliveries and feed data into the app's webhook pipeline labeled as belonging to another merchant's shop, since `WebhookMetadata.shop`/`topic` (built entirely from unauthenticated headers) is what host applications rely on to route/persist per-tenant data. Any host app that trusts `data.shop` from `ShopifyAPI::Webhooks::Registry.process` (as the gem's own documented flow instructs) inherits this cross-tenant confusion, matching a Critical-class cross-tenant access impact.

### Likelihood Explanation
Likelihood is high for any attacker who can install the target app on their own shop (an ordinary unprivileged action for any Shopify merchant) and control the raw HTTP request to the app's webhook endpoint (trivial — webhook endpoints are public URLs). No access to `api_secret_key`, access tokens, or victim credentials is required; only a single genuinely-signed `(body, hmac)` pair from the attacker's own shop is needed.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) inside the HMAC-signed material, or independently verify the `shop` header against an application-level record of the specific webhook subscription/shop the body was expected from before trusting it in `Registry.process`. At minimum, `Webhooks::Request#to_signable_string` should not be limited to `@raw_body` alone if `shop`/`topic` are used downstream as trusted identity fields, or `Registry.process` should require the caller to supply/verify the expected shop out-of-band (e.g., matching an active session) rather than trusting the header value implicitly.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and receives a real webhook, e.g., `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — verified via [5](#0-4) .
2. Attacker resends the exact same body `B` and header `H` to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which passes because `to_signable_string` only checks `B` against `H` — see [6](#0-5) .
4. The handler receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: ...)` — see [7](#0-6)  — and the host application processes/persists the attacker's data as if it belonged to the victim shop, achieving cross-tenant data injection/confusion.

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
