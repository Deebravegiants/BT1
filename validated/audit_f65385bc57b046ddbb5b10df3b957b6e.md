The analog here maps directly onto a rule pattern: **a field acted on but not covered by the HMAC**, exactly the same class of "verified bytes vs. bytes actually acted on" mismatch as the exchange-rate report (where the acted-upon state diverges from what was actually validated).

### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the `shop` (and `topic`/`webhook_id`) values used by the app to route/attribute the webhook are taken from unauthenticated HTTP headers that are never included in the signed payload.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shop-domain` header with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC by recomputing over `verifiable_query.to_signable_string` (the body) using the app's shared `api_secret_key`: [3](#0-2) 

`Registry.process` performs this HMAC check, then immediately trusts `request.shop` to build `WebhookMetadata` handed to the app's handler: [4](#0-3) 

The documented handler contract tells app authors that `data.shop` is simply "The shop domain of the webhook," with no caveat that it is unauthenticated: [5](#0-4) 

Because `api_secret_key` (the app's `client_secret`) is shared across every merchant who installs the app, any unprivileged attacker can install the app on their own store, capture a genuinely-signed webhook (valid body + HMAC, `shop-domain: attacker-shop.myshopify.com`), and replay it to the app's public webhook endpoint after only changing the `shop-domain` header to a victim tenant. The signature check still passes because it verifies bytes never touching the `shop` field, breaking the equality: `authenticated_shop (bound by HMAC) == shop_used_by_handler (from header)`.

### Impact Explanation
This crosses a tenant boundary using only a legitimately-issued (but replayed/edited) payload — no access token or secret is required beyond installing the app on an attacker-controlled shop, which is itself unprivileged. An app that keys any state (order ingestion, inventory sync, webhook dedup by shop, feature flags, billing counters) off `data.shop` can have attacker-controlled body content injected under a victim shop's identity, i.e. cross-tenant data injection/corruption.

### Likelihood Explanation
Requires only: (1) ability to install the target app on an attacker-owned shop (public, self-serve on Shopify), and (2) ability to intercept/replay one's own outbound HTTP header before it hits the app's public webhook endpoint. No credentials of the victim or the app are needed.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the HMAC-signed payload, or otherwise cryptographically tie the header-supplied shop to the verified body (e.g., verify the shop against records created via OAuth for that specific webhook subscription id) before constructing `WebhookMetadata`. At minimum, document loudly that `shop` is unauthenticated and must be independently cross-checked by the host app against known-installed shops.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook event (e.g. `orders/create`); Shopify POSTs to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid>` and an attacker-controlled body (attacker owns the shop, so they control the order/product content).
3. Attacker captures this request, changes only `x-shopify-shop-domain` to `victim-shop.myshopify.com`, and replays it to the same public webhook endpoint.
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes the HMAC over the unchanged raw body, which still matches — validation passes: [6](#0-5) 
5. `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, causing the host app to process attacker data under the victim's tenant identity.

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

**File:** docs/usage/webhooks.md (L10-18)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```
