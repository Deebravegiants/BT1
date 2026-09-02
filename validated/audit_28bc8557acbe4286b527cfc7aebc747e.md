### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are not covered by the HMAC signature, allowing shop-identity spoofing in `ShopifyAPI::Webhooks::Registry.process` - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Registry.process` validates only the HMAC of the body and then forwards the unauthenticated `shop` header value to the app's webhook handler as the tenant identity, breaking the binding: `hmac_verifies(body) == true` is treated as equivalent to `shop_header == authentic_source_shop`.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery`, whose contract is `hmac` + `to_signable_string`. The implementation is: [1](#0-0) 

```
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end
...
def shop
  T.cast(shopify_header("shop-domain"), String)
end
...
def to_signable_string
  @raw_body
end
```

`hmac` and `shop` are both derived from HTTP headers, but only `@raw_body` is what gets signed/verified (`to_signable_string`). `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `to_signable_string` (the body) and compares it to the `hmac-sha256` header, then `Registry.process` accepts the request as authentic if that check passes: [2](#0-1) 

The `request.shop` value used to build `WebhookMetadata` (and handed to the app's handler as the tenant/shop the event belongs to) is never part of the signed data - it is trusted purely because it arrived in a header alongside a body whose HMAC happens to be valid for *some* shop that installed the app with this `client_secret`.

### Impact Explanation
Because the HMAC only binds the *body*, not the sender's shop, any merchant who has installed the app (an "unprivileged" installer, not requiring the app's `client_secret` or any leaked token) can:
1. Trigger a real webhook delivery to their own store (a normal, permitted action) and capture the resulting valid `(raw_body, hmac-sha256)` pair sent by Shopify to the app's public webhook endpoint.
2. Replay that exact body/HMAC pair to the same endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header for a victim shop.
3. `HmacValidator.validate` still returns `true` (body/HMAC untouched), and `Registry.process` dispatches the handler with `shop: <victim-shop>` populated from the forged header.

Any app logic that keys off `WebhookMetadata#shop` (e.g., looking up/activating that shop's session, writing tenant-scoped data, running mandatory GDPR handlers like `customers/redact` against the wrong shop) executes under a spoofed shop identity — a cross-tenant identity confusion reachable entirely from the public internet without possessing any of the excluded credentials.

### Likelihood Explanation
Reaching the vulnerable path requires only: (a) the ability to install the target public app on an attacker-controlled shop to obtain one valid `(body, hmac)` pair (a standard, unprivileged action), and (b) sending a normal HTTP POST to the app's public webhook endpoint with a modified header. No secret material, session, or elevated privileges are needed, so likelihood is high given a listening webhook endpoint.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed material, or otherwise cryptographically bind them to the request (e.g., verify `shop` against the session/store that is expected for the topic being processed) before trusting `request.shop` for tenant-scoped actions. At minimum, document prominently that `Registry.process`'s `shop` field is not authenticated by the HMAC, and instruct implementers to independently corroborate the shop identity (e.g., cross-check against a known/installed shop list) before using it for tenant-sensitive operations.

### Proof of Concept
1. Install the target Shopify app on attacker-owned shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) so Shopify POSTs `raw_body` + `X-Shopify-Hmac-Sha256: H` to the app's public webhook endpoint.
2. Capture `raw_body` and `H` from that legitimate delivery.
3. Replay: `POST /webhooks` with the same `raw_body`, same `X-Shopify-Hmac-Sha256: H`, but `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a request where `hmac` matches (`to_signable_string` == `raw_body`, unchanged) and `shop` == `"victim.myshopify.com"`.
5. `ShopifyAPI::Webhooks::Registry.process(request)` passes `Utils::HmacValidator.validate(request)` (body unmodified) and invokes the app handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the app to act as if the event originated from the victim's store.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
