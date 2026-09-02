### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant shop-identity spoofing on genuine webhook deliveries - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value exposed to app handlers directly from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, while `ShopifyAPI::Utils::HmacValidator` (via `to_signable_string`) validates the HMAC only over the raw request body. The header carrying tenant identity is never part of the signed material, so the value the app trusts as "which shop this webhook belongs to" is not bound to the HMAC that proves "this webhook is authentic."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop` is read straight from the (unsigned) header: [2](#0-1) 

`Registry.process` verifies HMAC using exactly that signable string, then forwards `request.shop` unchanged to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the body) and the app secret, never touching headers: [4](#0-3) 

This breaks the intended identity binding:
`HMAC-verified(body)` ≠ `shop used by the app as the tenant key (data.shop)`.

Because the shop header is excluded from the signed bytes, a `(body, hmac)` pair that is genuinely valid for shop A can be replayed with the `x-shopify-shop-domain` header rewritten to shop B, and it will still pass `HmacValidator.validate` unchanged — the gem has no mechanism to detect the substitution. Any external actor who can obtain one genuine, cryptographically-signed webhook (e.g., by installing the app on their own store, which is normal, unprivileged behavior for any Shopify Partner app) can then relabel that request as belonging to an arbitrary victim shop domain and deliver it to the app's public webhook endpoint.

The gem's own documentation confirms `data.shop` is meant to be trusted as the tenant identifier by consuming apps: [5](#0-4) 

### Impact Explanation
This crosses the cross-tenant boundary: an unprivileged party (an attacker who is merely a legitimate app installer on their own store) can cause the app to process webhook data under a different shop's identity, despite HMAC verification "passing." Any app logic keyed off `data.shop` — routing background jobs, updating per-tenant records, invalidating caches, or gating side effects — can be forced to act as if the event came from a shop the attacker does not control. This matches the Critical "cross-tenant access" impact category, since the shop/tenant binding that the HMAC check is supposed to guarantee is not actually enforced by this gem.

### Likelihood Explanation
Likelihood is realistic but requires the attacker to first obtain at least one genuinely signed webhook payload of their own (e.g., by installing the target app on their own development/store account, which is a normal unprivileged action for any Shopify app that is publicly listed or otherwise installable). Once obtained, replaying it with a modified header requires only a single HTTP request to the app's public webhook endpoint, with no need for the `client_secret` or any credential.

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically tie the verified HMAC to the shop the request claims to be from — e.g., include the `shop-domain` header in `to_signable_string` (matching what Shopify actually signs), or reject/re-verify shop identity against an independently known value (such as the shop tied to the webhook subscription/registration) rather than trusting the header value forwarded from `Request#shop`.

### Proof of Concept
1. Attacker installs the target Partner app on their own store `attacker.myshopify.com`, triggering a genuine webhook (e.g. `orders/create`) with body `B` and valid header `X-Shopify-Hmac-Sha256: HMAC(secret, B)`.
2. Attacker captures this request, then re-sends it to the app's webhook endpoint with the header changed to `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (body `B` and the HMAC header left untouched).
3. `ShopifyAPI::Webhooks::Request.new` parses `shop` from the (now spoofed) header: [2](#0-1) 
4. `Registry.process` calls `HmacValidator.validate(request)`, which recomputes the HMAC only over `@raw_body` (`B`) — unchanged from step 1 — so validation succeeds: [3](#0-2) 
5. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and `body: B`, even though the event never originated from and was never authorized by that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
