### Title
Webhook shop identity spoofing due to shop-domain header not covered by HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` verifies only covers the raw request body. An attacker who can obtain one genuinely-signed webhook (e.g. by installing the app on their own shop) can replay that exact body/HMAC pair while substituting an arbitrary victim shop domain in the header, and the signature check still passes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns `@raw_body`: [1](#0-0) 

Meanwhile `shop` is read straight from an attacker-controlled HTTP header and is never included in the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` only, so the `shop` header is fully outside the authenticated payload: [3](#0-2) 

`Registry.process` checks the HMAC and, once it passes, forwards `request.shop` unchanged into `WebhookMetadata` for the app's handler to act on: [4](#0-3) 

The gem's own documentation instructs developers to treat `data.shop` as the authoritative per-shop key for downstream processing (e.g. enqueuing shop-scoped jobs), reinforcing that this field is trusted as an identity binding: [5](#0-4) 

The broken identity binding, as an equality that should hold but doesn't:
`shop_bound_by_hmac(raw_body) == shop_used_as_tenant_key(header)` — the left side doesn't exist because the header is never part of the signed bytes, so the two can diverge freely.

### Impact Explanation
Any actor who can install the app on at least one shop (a normal, unprivileged action for a public/embedded Shopify app) will receive legitimately Shopify-signed webhooks for that shop. Because the shop-domain header is not part of the signed payload, that same signed body can be replayed to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to any victim shop. `Registry.process` will validate the HMAC successfully and hand the handler a `WebhookMetadata` claiming to be the victim shop while carrying attacker-controlled body content. Any host application following the gem's documented pattern of keying persistence/business logic off `data.shop` will perform actions against the wrong tenant using attacker-supplied data — a cross-tenant integrity/confidentiality violation achieved without ever obtaining the victim's access token or `client_secret`.

### Likelihood Explanation
Exploitation only requires the ability to install the app once (satisfying "unprivileged internet user" — installing a public Shopify app requires no special access) and the ability to send an HTTP request to the app's public webhook endpoint with a modified header, which is standard and requires no cryptographic secret. The vulnerable code path (`Request#shop`, `to_signable_string`, `HmacValidator.validate`, `Registry.process`) is exercised on every webhook processed by any app using this gem's documented webhook flow.

### Recommendation
Include the `shop` (and ideally `topic`) values in the signed material verified for webhooks, or otherwise cryptographically bind the shop-domain header to the payload before trusting it (e.g., require the caller to independently verify `request.shop` against a shop they already have an active, authenticated session/webhook subscription for, rather than trusting the header at face value). At minimum, document prominently that `data.shop` from `WebhookMetadata` is unauthenticated and must not be used as a lookup key without additional verification (e.g., cross-checking against the shop's currently registered webhook subscription id server-side).

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and configures a webhook topic (e.g. `orders/create`).
2. Shopify sends a legitimately signed webhook request to the app: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's `client_secret`), and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures this request and resends it to the same webhook endpoint, keeping body `B` and header `H` unchanged, but replacing `x-shopify-shop-domain` with `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) — validation succeeds because `B` and `H` are unchanged.
5. `handler.handle` is invoked with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

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

**File:** docs/usage/webhooks.md (L10-26)
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
```
