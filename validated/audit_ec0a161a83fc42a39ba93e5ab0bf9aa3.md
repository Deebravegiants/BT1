Confirmed: the HMAC in `ShopifyAPI::Webhooks::Request` covers only the raw body, while the `shop`, `topic`, and `webhook_id` fields the app relies on for tenant identification and dispatch come from unauthenticated headers.### Title
Webhook `shop-domain` and `topic` identity is trusted from unauthenticated headers while HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw HTTP body only, but the `shop`, `topic`, and `webhook_id` values that `Registry.process` uses to select the handler and identify the tenant are read straight from unauthenticated HTTP headers. This breaks the identity binding `bytes verified == bytes trusted`: the app verifies the body's integrity/origin but trusts headers that were never included in that verification.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` verifies the HMAC exclusively against that signable string: [2](#0-1) 

Meanwhile `Registry.process` uses `request.topic` to look up the handler and forwards `request.shop`/`request.topic`/`request.webhook_id` into `WebhookMetadata`, which is the tenant-identifying data the host app acts on: [3](#0-2) 

`request.shop`, `request.topic`, and `request.webhook_id` are all pulled directly from HTTP headers with no cryptographic binding to the verified body: [4](#0-3) 

Since every shop that installs the same app shares one HMAC secret (`Context.api_secret_key`), the HMAC over the body is valid for **any** shop's payload with that same body content — it does not bind the body to a specific shop or topic. An unprivileged actor who controls a shop where the app is installed (a legitimate, non-privileged tenant) receives genuine webhook deliveries for their own shop, each with a valid `hmac-sha256` over the body. That same `(raw_body, hmac)` pair remains valid when replayed to the app's webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header swapped to point at a different, victim shop, because those header values play no part in the signature check.

This equality is broken:
`shop/topic identified for dispatch and tenant attribution (request.shop / request.topic)` != `shop/topic bound by the verified signature (to_signable_string == raw_body only)`

### Impact Explanation
This is a cross-tenant identity confusion at the gem level: `Registry.process` and the resulting `WebhookMetadata.shop`/`topic` are the only tenant/topic signals the host application receives from this library after "verification." An attacker who legitimately controls one shop's webhook traffic can forge the shop/topic attribution of any body they can produce for their own shop (e.g., an `orders/create` payload they trigger themselves) and cause it to be processed as if it came from another shop or another topic that expects a similarly-shaped payload — i.e., cross-tenant access/data confusion, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Medium-High: the attacker needs only a shop with the target app installed (which webhook subscribers legitimately have) to capture one valid `(body, hmac)` pair from their own real webhook deliveries, then replay it to the app's public webhook endpoint with modified `shop-domain`/`topic`/`webhook-id` headers — no access to `api_secret_key` or any privileged token is required.

### Recommendation
Include `shop-domain`, `topic`, and `webhook_id` in the HMAC-signable material (or otherwise bind them cryptographically, e.g. as Shopify does by having the platform-side integrity check cover a canonical representation including these identifiers), so that `Utils::HmacValidator.validate` fails if any of these header values are altered relative to what was originally signed by Shopify. At minimum, document/require host apps to cross-check `request.shop` against a known/expected shop before trusting `WebhookMetadata`, but the correct fix belongs in this gem's `Request#to_signable_string`.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, both webhooks routed to the same handler via `ShopifyAPI::Webhooks::Registry.process`.
2. Attacker triggers a real event on their own shop (e.g. `orders/create`), and their app endpoint receives a genuine webhook with headers:
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
   - `x-shopify-hmac-sha256: <valid HMAC of body>`
3. Attacker replays the identical raw body and `hmac-sha256` value to the same endpoint, but changes the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (per `lib/shopify_api/utils/hmac_validator.rb:12-22`) still succeeds because it only checks the body against the shared secret.
5. `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: <attacker's body>, ...)`, causing the host app to process attacker-supplied data under the victim shop's tenant identity.

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
