### Title
Webhook `shop-domain` header is trusted for tenant routing without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by HMAC-verifying the raw request **body**. The `shop`/`shop-domain` field, which the gem hands to the app's handler as the tenant identifier, is read directly from an HTTP header that is not part of the signed data. An attacker who can obtain one valid `(body, HMAC)` pair for the target app (trivially, by installing the app on their own store and triggering a webhook with attacker-chosen content) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `shop-domain` header for a victim shop. The signature still validates, and the gem hands the handler a `WebhookMetadata` claiming the body belongs to the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic binding to the body or to the HMAC value: [2](#0-1) 

`Registry.process` verifies only `Utils::HmacValidator.validate(request)` (which in turn HMACs `request.to_signable_string`, i.e., the body only), and then immediately forwards `request.shop` to the handler as the tenant identifier: [3](#0-2) 

`HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` (the body) and compares it to the `hmac` header — the `shop` header never enters this computation: [4](#0-3) 

The identity binding that should hold is:
`shop header used for tenant routing == shop that produced/authorized this exact HMAC-signed body`

Because only the body is signed, this equality is not enforced: `shop` can be swapped for any string while `body` and `hmac` remain a valid, previously-observed pair for a *different* shop that also uses the same app (and therefore the same `api_secret_key`, which is shared across all installations of a given app).

### Impact Explanation
This breaks the tenant boundary that app developers are documented to rely on: the docs instruct handlers to key persistence and business logic off `data.shop` alongside `data.body`, treating both as verified once `HmacValidator.validate` passes: [5](#0-4) 

An attacker who has any working relationship with the target app (e.g., a free trial install on their own store — an unprivileged, ordinary flow) can capture a legitimate `(raw_body, hmac)` pair by triggering a webhook with attacker-chosen field values (e.g., `products/update` with a crafted title/body), then replay it to the app's public webhook endpoint with the `shop-domain` header changed to a victim's domain. The app will process attacker-controlled body content attributed to the victim tenant, corrupting or spoofing cross-tenant data — a **cross-tenant access** condition.

### Likelihood Explanation
Exploitation requires: (1) knowledge of the app's public webhook URL (typically discoverable/static per app), (2) the ability to generate at least one genuine webhook with attacker-chosen body content via the attacker's own legitimate/trial installation of the app (a normal, low-privilege action, not requiring the app's `client_secret` or a victim's access token), and (3) the ability to send an arbitrary HTTP request with custom headers to that endpoint (any internet user). No credentials of the app or the victim are needed. This is a realistic, moderately likely scenario given webhook endpoints are internet-facing by design.

### Recommendation
Do not treat `shop`/`shop-domain` (or `topic`, `api-version`, `webhook-id`) as trusted once only the body's HMAC has been validated. At minimum:
- Document/require host applications to independently verify that `shop` corresponds to a shop with an active, matching webhook subscription (e.g., cross-check against `webhook_id` stored at registration time) before trusting `data.shop`.
- Where feasible, bind `shop` into the value that is HMAC-verified (e.g., validate that the `webhook_id` returned in the request maps to the claimed `shop` via a server-side lookup) rather than trusting the header verbatim.
- Update `ShopifyAPI::Webhooks::Request`/`Registry` and the accompanying documentation to explicitly warn that `shop-domain` is not covered by the HMAC and must not be used as the sole tenant key without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` (ordinary, unprivileged onboarding).
2. Attacker triggers a webhook event (e.g., updates a product) so Shopify sends a webhook to the app's endpoint with body `B` and a valid `x-shopify-hmac-sha256` header `H`, plus `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker intercepts/replays this exact request to the same endpoint, but changes only the `x-shopify-shop-domain` header to `victim.myshopify.com` (keeping body `B` and HMAC `H` identical).
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "x-shopify-shop-domain" => "victim.myshopify.com", "x-shopify-hmac-sha256" => H})` is constructed.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only HMACs `B` (`to_signable_string`), matching `H`.
6. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to act on attacker-supplied data as if it originated from `victim.myshopify.com`.

**Note on limitations:** I was unable to fully verify how downstream consumers (e.g., the `shopify_app` reference implementation) mitigate this at the framework level, since that logic lives outside this gem. My analysis is scoped strictly to `lib/shopify_api/webhooks/**` and `lib/shopify_api/utils/hmac_validator.rb`, per the in-scope rules; whether a specific host application adds its own shop/webhook_id cross-checks is outside this gem's code.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
