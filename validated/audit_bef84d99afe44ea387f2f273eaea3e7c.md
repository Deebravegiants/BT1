I have enough evidence to confirm this analog. The `to_signable_string` for webhook `Request` only signs `@raw_body` [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read from unauthenticated HTTP headers [2](#0-1) , and `Registry.process` forwards `request.shop` directly into the handler's tenant-identifying data after only checking the body HMAC [3](#0-2) .

### Title
Webhook HMAC validates only the request body, not the `shop-domain` header, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC verified by `Utils::HmacValidator.validate` in `Registry.process` binds solely to the JSON body bytes [1](#0-0) . The `shop` value that `Registry.process` passes on to the application's webhook handler as the tenant identifier is read from the `x-shopify-shop-domain` header, which is completely outside the HMAC's coverage [4](#0-3) . This breaks the identity binding `HMAC(secret, signed_bytes) == HMAC(secret, request.shop ++ raw_body)` that a tenant-scoped webhook consumer needs; in reality it only enforces `HMAC(secret, signed_bytes) == HMAC(secret, raw_body)`, with `request.shop` unconstrained.

### Finding Description
`Registry.process` does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
``` [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, which for `Webhooks::Request` is `@raw_body` alone [5](#0-4) [1](#0-0) . Since Shopify's own HMAC scheme for webhooks only ever signs the raw body (this is documented Shopify behavior, not a gem-specific defect in isolation), any legitimately-signed webhook payload one attacker-controlled shop receives from Shopify (e.g., by installing the target app on their own store and triggering any webhook topic) carries a valid HMAC for that exact body. Because the gem never binds `shop-domain`, `topic`, or `webhook-id` headers into the signed bytes, an attacker can resend that captured request to the same app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain (or `x-shopify-webhook-id`/`topic` altered), and `Registry.process` will pass validation and hand the handler a `WebhookMetadata` claiming to originate from the victim shop.

Any host application that uses `WebhookMetadata#shop` to scope database writes, cache invalidation, uninstall/redact handling, or other per-tenant side effects (the intended and documented use of this field) will process attacker-controlled data under the wrong shop's identity, because this gem's own `Request`/`Registry` code presents `shop` as if it were verified alongside the body, when it is not.

### Impact Explanation
This lets an unprivileged internet user who can install the target app on any shop (including their own, free, trial shop) forge webhook deliveries that the host application will attribute to an arbitrary other shop using the same app, without any credentials for that victim shop. This crosses the tenant boundary the gem's webhook verification is supposed to enforce, matching the Critical "cross-tenant access" impact category, since the merchant-facing effects of `customers/redact`, `shop/redact`, order/product mutations, etc. would be attributed to and applied against a shop the attacker never authenticated to.

### Likelihood Explanation
Exploitation requires only: (1) the attacker installs the vulnerable app on a shop they control (many Shopify apps offer free installs/trials), (2) captures one legitimate webhook delivery with its raw body and valid HMAC, and (3) replays it to the app's public webhook endpoint with a rewritten `shop-domain` (and optionally `webhook-id`) header. No secrets, tokens, or victim cooperation are needed, making this practically reachable by any internet user targeting an app built on this gem.

### Recommendation
Bind the identifying headers into the signed material, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the verified signature before exposing them to handlers — e.g., include `shop-domain`, `topic`, and `webhook-id` in `to_signable_string`, or require the host application look up the expected shop domain out-of-band (from its own webhook subscription registration) rather than trusting the header value forwarded in `WebhookMetadata`. At minimum, the docs/API should make explicit that `WebhookMetadata#shop` is unauthenticated and must not be used for tenant-scoped actions without additional verification.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own shop "attacker.myshopify.com" and
#    receives (or triggers) a legitimate webhook, e.g. customers/redact, with body B
#    and a correctly computed HMAC H = HMAC-SHA256(api_secret_key, B).

# 2. Attacker resends the exact same body B and HMAC H to the app's webhook
#    endpoint, but swaps the shop-domain header to the victim shop:
headers = {
  "x-shopify-topic" => "customers/redact",
  "x-shopify-hmac-sha256" => H,               # unchanged, still valid for body B
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
  "x-shopify-webhook-id" => "attacker-controlled-id",
}
request = ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: headers)

# 3. Registry.process validates the HMAC (passes, since only B is signed) and
#    invokes the handler with WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle receives shop = "victim-shop.myshopify.com" despite the
#    request never having been authenticated for that shop.
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
