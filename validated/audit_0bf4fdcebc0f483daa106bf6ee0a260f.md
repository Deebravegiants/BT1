### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) header values are trusted for tenant routing while the HMAC only signs the raw body, allowing cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body via `Utils::HmacValidator.validate(request)`. The `shop` value that is handed to the app's handler and used for tenant identification, however, comes from the unauthenticated `X-Shopify-Shop-Domain` header and is never included in the signed material. Because a single app-wide `api_secret_key` is used to sign webhooks for *every* installed shop, any actor who legitimately installs the app on their own store can capture a validly-signed webhook (body + HMAC) and replay it with the `shop-domain` header changed to a victim shop, producing a webhook that passes HMAC validation but is misattributed to the victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is fully attacker-controllable and is not part of `to_signable_string`.

`HmacValidator.validate` only checks the HMAC over `verifiable_query.to_signable_string` (the raw body) against `Context.api_secret_key`: [3](#0-2) 

`Registry.process` performs this single check and then immediately trusts `request.shop` (along with `topic`, `api_version`, `webhook_id`) to build the `WebhookMetadata` passed to the host application's handler: [4](#0-3) 

The equality this breaks is: `shop bound by HMAC == shop used for tenant routing`. In reality, the HMAC only binds `body`, while `shop` (the tenant identity) is taken from an unsigned header. Since `Context.api_secret_key` is one value per app, shared across all shops that install it, any HMAC computed with that key is valid *regardless of which shop it was originally issued for*. This is directly analogous to the reported bug class: a value (webhook `shop`) is *acted on* by downstream logic (tenant dispatch) without being *covered* by the cryptographic binding (HMAC), just as `getPriceFromAMM` acted on `getAmountsOut` values that were not bound to a manipulation-resistant source.

### Impact Explanation
This enables cross-tenant confusion: an attacker who installs the app on their own store (a normal, unprivileged action any internet user can perform for a public Shopify app) receives real webhooks HMAC-signed with the app's single, shared `api_secret_key`. By replaying the exact `raw_body`/HMAC pair while swapping the `shop-domain` header to a victim's shop domain, the attacker gets `Registry.process` to accept the request as valid and hand `WebhookMetadata` to the host app's handler with the victim's shop populated. If the host application (as is standard practice, and exactly the intended use of `WebhookMetadata#shop`, per `test/webhooks/registry_test.rb`) uses this `shop` value to look up per-tenant records, credentials, or trigger tenant-scoped side effects, the attacker can inject or manipulate data attributed to a shop they do not control — a cross-tenant access impact.

### Likelihood Explanation
Likelihood is high for any app that is publicly installable (the normal case for Shopify apps): obtaining a genuine signed webhook only requires the attacker to install the app on their own free/dev store and observe one webhook delivery, at which point they can replay it against arbitrary shop identifiers indefinitely (subject to body content matching intended payload) without ever needing `api_secret_key`, an access token, or any privileged account.

### Recommendation
Include the shop domain (and any other value used to make trust decisions, e.g. `topic`) in the HMAC-verified material — or independently ensure the shop domain in the webhook header corresponds to a shop actually known to have installed the app for that specific webhook body — rather than only validating the request body.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook (e.g. `orders/create`) and captures the raw body `B` along with the valid `X-Shopify-Hmac-SHA256` header `H`, both signed using the app's shared `Context.api_secret_key`.
3. Attacker replays a webhook POST to the app's webhook endpoint with:
   - `X-Shopify-Hmac-SHA256: H`
   - body: `B`
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `H` matches `HMAC(B, api_secret_key)` — the shop header is never part of that check (see `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:12-22`).
5. `WebhookMetadata.new(... shop: request.shop ...)` is built with `shop = "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`) and dispatched to the app's handler, which processes/stores data as if it legitimately originated from the victim's shop.

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
