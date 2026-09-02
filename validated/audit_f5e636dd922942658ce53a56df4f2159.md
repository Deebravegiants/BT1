I have confirmed the root cause with sufficient evidence to finalize the analog finding.

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity is not covered by the HMAC signature, allowing tenant/topic spoofing via header substitution on a replayed webhook - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` verifies exclusively the payload bytes, never the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers. `Registry.process` nonetheless takes `request.shop` (and the other unauthenticated headers) straight from those headers and hands them to the app's `WebhookHandler` as trusted identity fields inside `WebhookMetadata`, which the documentation explicitly tells app authors to use for shop/tenant identification and job dispatch.

### Finding Description
The identity binding that should hold is: `shop header == shop cryptographically bound to the signed bytes`. It does not hold here.

- `Request#hmac` reads `shopify-hmac-sha256`/`x-shopify-hmac-sha256`. [1](#0-0) 
- `Request#shop` reads `shopify-shop-domain`/`x-shopify-shop-domain`, a plain unauthenticated header. [2](#0-1) 
- `Request#to_signable_string` — the value actually HMAC-verified — is only `@raw_body`; it excludes `shop`, `topic`, `webhook_id`, and `api_version` entirely. [3](#0-2) 
- `HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` only (i.e., the body), and compares it to the received signature — the shop/topic/webhook-id headers play no role in the check. [4](#0-3) 
- `Registry.process` validates the HMAC and then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to build `WebhookMetadata`, which is passed to the app's handler. [5](#0-4) 
- `WebhookMetadata` is a plain struct with no additional integrity check on `shop`. [6](#0-5) 
- The gem's own documentation instructs app authors to key their business logic (e.g., background job dispatch) directly off `data.shop`, i.e., to treat it as the authenticated tenant identifier. [7](#0-6) 

Because only the body bytes are signed, any party who can obtain one validly-signed webhook body+HMAC pair for topic T (for example, a merchant receiving genuine webhooks for their own store, or any attacker who can otherwise get one authentic `(body, hmac)` pair from Shopify for any shop/topic) can resend that exact body+hmac to a victim app's webhook endpoint while substituting `shop-domain` (and/or `topic`, `webhook_id`) headers for a different tenant. `HmacValidator.validate` still returns `true` because it only checks the untouched body against the untouched HMAC; `Registry.process` then dispatches to the handler with the attacker-chosen `shop` value in `WebhookMetadata`, causing the host application to act on/store data under the wrong tenant.

### Impact Explanation
This breaks the identity binding `authenticated-webhook-shop == body signed by that shop's data`. An app that trusts `data.shop` (as the docs tell it to) to select which merchant's database row/session/job queue to write into can be made to apply another shop's webhook body under a different shop's identity, or to accept a spoofed `topic`/`webhook_id`, causing cross-tenant data confusion. This matches the Critical category of cross-tenant access enabled purely through this gem's own verification logic.

### Likelihood Explanation
Exploitation requires the attacker to already possess one legitimately-signed `(body, hmac)` webhook pair — which is trivial for any unprivileged user who owns a Shopify store and receives real webhooks from their own shop, since Shopify signs the same way for every merchant with the app's single shared `api_secret_key`. No access token, `client_secret`, or privileged account is required; only network access to POST to the app's public webhook callback URL. This is a realistic unprivileged-internet-user attack path.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signed material (or otherwise cryptographically bind them to the body), so `HmacValidator.validate` fails whenever any of these identity-bearing headers are altered relative to what Shopify actually signed. At minimum, document prominently that `Request#shop`/`#topic`/`#webhook_id`/`#api_version` are NOT integrity-protected by `HmacValidator.validate` and must not be trusted as tenant identifiers without additional verification (e.g., cross-checking against a known list of shops with an active webhook subscription for that specific `webhook_id`).

### Proof of Concept
1. Legitimate webhook delivery for `shop-a.myshopify.com`, topic `orders/create`, arrives with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker (who owns `shop-a` and thus legitimately received this webhook) resends an HTTP POST to the victim app's public webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256: H`, but with `x-shopify-shop-domain: shop-b.myshopify.com` substituted.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `to_signable_string` still returns `B`. [3](#0-2) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B)` and compares it to `H` — it matches, since the body was untouched. [8](#0-7) 
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", body: parsed(B), ...)` and calls the app's handler. [9](#0-8) 
6. The host app, following the documented pattern of dispatching work keyed on `data.shop`, processes `shop-a`'s order data under `shop-b`'s tenant context. [10](#0-9)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
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

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
