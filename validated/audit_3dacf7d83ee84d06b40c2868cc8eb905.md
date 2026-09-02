### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts the unauthenticated `shop-domain` header to identify the tenant the event belongs to. Because the shop identity is never part of the signed material, any actor able to produce one valid `(body, hmac)` pair for the app's shared `api_secret_key` can relabel that payload as belonging to an arbitrary victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw JSON body: [1](#0-0) 

`Request#shop` is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is never included in the signable string: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and, if it passes, hands `request.shop` straight to the handler as the authenticated tenant identifier, with no independent check that this shop is one the app has installed or that it matches any known/registered relationship: [3](#0-2) 

`HmacValidator.validate` computes the signature using `Context.api_secret_key`, which is the app-level client secret shared across *every* merchant that installs the app — it is not a per-shop secret: [4](#0-3) 

Binding broken (as an equality that should hold but doesn't):
`hmac_signed_bytes` (raw body only) ≠ `identity_bytes_acted_on` (`shop` header value trusted by `Registry.process`/`WebhookMetadata`).

Because the same `api_secret_key` authenticates webhooks for all shops that have installed the app, an unprivileged attacker who installs the app on their own store (a normal, unprivileged action any Shopify merchant can take) can capture a legitimately-signed `(raw_body, x-shopify-hmac-sha256)` pair from their own shop's webhook delivery, then replay that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header for a victim shop. `HmacValidator.validate` will still succeed (the body and secret are unchanged), and `Registry.process` will dispatch the payload to the handler labeled with the attacker-chosen shop, e.g. `WebhookMetadata.shop`.

### Impact Explanation
This breaks the tenant-identity binding the host application relies on: `data.shop` is documented as the authenticated shop domain of the webhook, and the gem's own usage docs instruct developers to key their business logic off of it (`shop_domain: data.shop`) without additional verification, since the gem is expected to have already authenticated the webhook: [5](#0-4) 

An attacker can inject fabricated or replayed event data attributed to a victim shop, causing the host app to process cross-tenant data under the wrong shop's identity (e.g., triggering shop-specific side effects, corrupting per-shop state, or spoofing events for a shop the attacker does not control). This matches the Critical "cross-tenant access" impact category, since the identity boundary between tenants (shops) is not cryptographically enforced by this gem despite integrity validation appearing to have occurred.

### Likelihood Explanation
High. No privileged credentials, leaked secrets, or TLS interception are required. Any user can sign up for and install a Shopify app on their own store (this is the normal "unprivileged internet user" flow for public/development apps), receive a genuinely-signed webhook, and replay it with a modified shop header directly against the app's public webhook endpoint. The only requirement is that the app process webhooks over HTTP with a handler that trusts `data.shop`, which is exactly the documented usage pattern.

### Recommendation
The gem should not allow the shop domain to be trusted purely from an HTTP header divorced from the authenticated payload. Options:
- Extend `Webhooks::Request#to_signable_string` (or add an additional check in `Registry.process`) to bind the `shop-domain` header into the material verified by the HMAC, or otherwise cryptographically tie header values to the signed body.
- At minimum, document prominently (and ideally enforce in `Registry.process`) that host applications must cross-check `request.shop` against a shop known to have `register`ed for that specific webhook topic before trusting it, since the current API surface encourages developers to treat `data.shop` as authenticated.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw body `B` and the resulting `X-Shopify-Hmac-Sha256: H` header sent by Shopify (computed with the app's single, shared `api_secret_key`).
2. Attacker sends `POST /callback/orders/create` to the target app with:
   - Body: `B` (unchanged)
   - Headers: `x-shopify-hmac-sha256: H`, `x-shopify-topic: orders/create`, `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: ...)` is constructed and passed to `Registry.process`.
4. `Utils::HmacValidator.validate` recomputes HMAC over `B` using `Context.api_secret_key` and it matches `H`, so validation succeeds (`lib/shopify_api/utils/hmac_validator.rb:12-22`, `lib/shopify_api/webhooks/registry.rb:190`).
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though the event never originated from that shop — demonstrating the identity-binding break.

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

**File:** docs/usage/webhooks.md (L10-29)
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
