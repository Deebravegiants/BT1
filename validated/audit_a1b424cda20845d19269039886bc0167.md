### Title
Webhook HMAC covers only the request body, not the `shop-domain`/`topic`/`webhook-id` headers used for tenant routing — cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so `Utils::HmacValidator.validate` authenticates nothing but the *bytes of the body*. The `shop`, `topic`, `webhook_id`, and `api_version` values that `Registry.process` hands to the app's webhook handler as the tenant/routing identity are read straight from unauthenticated HTTP headers and are never part of the signed material. This is the same class of bug as the reported `FantiumNFTV1._owners` issue: the code *verifies* one piece of state (raw body bytes against an HMAC) while *acting on* a different, unverified piece of state (the shop/topic/webhook-id headers) — an identity binding that should hold (`verified bytes == bytes that determine tenant`) does not.

### Finding Description
`HmacValidator.validate` computes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it to the `hmac` field of the query object: [1](#0-0) 

For webhooks, `to_signable_string` is defined to return only `@raw_body`: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` — the values used to decide *which tenant/shop* the webhook applies to — are pulled from headers that are completely outside the HMAC computation: [3](#0-2) 

`Registry.process` validates the HMAC and then dispatches to the handler using these unauthenticated header values as the tenant identity: [4](#0-3) 

Because the HMAC secret (`Context.api_secret_key`, i.e. the app's client secret) is the same for every shop that has the app installed, any merchant who installs the app on their own store can capture a legitimately-signed `(raw_body, hmac)` pair delivered to their own webhook endpoint. Since the header values (`shop-domain`, `topic`, `webhook-id`, `api-version`) are not covered by the signature, that same `(raw_body, hmac)` pair remains valid when replayed to the app's public webhook controller with arbitrary attacker-chosen headers — e.g. a different victim `shop-domain`. `HmacValidator.validate` still returns `true` because it only checks the body bytes, and `Registry.process` will invoke the handler believing the event legitimately originates from the victim shop: [5](#0-4) 

This is documented as the intended flow for app authors, who are told to trust `data.shop` from the processed webhook without any additional cross-check: [6](#0-5) 

### Impact Explanation
This breaks a tenant-isolation identity binding: `verified_bytes (raw body) == bytes_that_determine_shop_identity (shop-domain header)`. An attacker who is a legitimate, low-privileged merchant with the app installed on their own store can forge a webhook attributed to a different shop by reusing a genuinely-signed body/HMAC pair with a spoofed `shop-domain` header (and arbitrary `topic`/`webhook-id`). Depending on how the host application uses `data.shop`/`data.topic` (e.g. `shop/redact`, `customers/data_request`, `app/uninstalled` handling, cache invalidation, billing/session updates keyed by shop), this can lead to cross-tenant data manipulation or spoofed lifecycle events for a shop the attacker does not control — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Requires only that the attacker operate one legitimate low-privilege installation of the target app (to obtain one valid signed body/HMAC pair) and be able to POST directly to the app's public webhook endpoint with custom headers — no `api_secret_key`, access token, or privileged account for the victim shop is needed. This is a realistic, unprivileged-internet-facing scenario since webhook endpoints are, by design, exposed to POSTs from outside the app's authenticated session flow.

### Recommendation
Bind the identity fields into the signed material (or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the verified body) instead of trusting header values that live outside the HMAC. At minimum, `Utils::HmacValidator`/`Webhooks::Request` should incorporate the `shop-domain` (and ideally `topic`/`webhook-id`) into `to_signable_string`, or the library should provide/require a secondary verification step (e.g., cross-checking the shop against an offline session store) before dispatching to handlers, and documentation should not tell integrators that `Registry.process` alone "will verify the request did indeed come from Shopify" for a specific shop.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and triggers any registered webhook (e.g., `orders/create`), capturing the delivered request: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid, since `H = HMAC(client_secret, B)`).
2. Attacker sends a new HTTP POST directly to the app's public webhook route with:
   - Body: the exact same bytes `B`
   - Headers: `X-Shopify-Hmac-Sha256: H` (unchanged), `X-Shopify-Shop-Domain: victim-shop.myshopify.com`, `X-Shopify-Topic: shop/redact` (or any topic the attacker chooses), `X-Shopify-Webhook-Id: <arbitrary>`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, B)` and matches `H` — validation passes because only `B` is checked [2](#0-1) .
4. The handler is invoked with `WebhookMetadata.new(topic: "shop/redact", shop: "victim-shop.myshopify.com", ...)` [7](#0-6) , causing the host application to act as if a legitimate `shop/redact` (or other) event was received from `victim-shop.myshopify.com`, even though that shop never sent it.

### Citations

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
