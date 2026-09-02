Based on my investigation, I found a concrete instance of the exact bug class described in the rules: a field acted on (the shop identity) but not covered by the HMAC.

### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the `shop` (and `topic`/`webhook_id`) values are read directly from HTTP headers that are never included in that signature. `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` to construct the `WebhookMetadata` passed to the app's handler, breaking the intended binding: `hmac == HMAC(body)` should imply `shop == the shop the body actually belongs to`, but the gem only proves `hmac == HMAC(body)`, not `hmac == HMAC(body, shop)`.

### Finding Description
`to_signable_string` only returns `@raw_body`: [1](#0-0) 

But `shop` is pulled straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header with no cryptographic tie to the signed body: [2](#0-1) 

`HmacValidator.validate` only ever recomputes the signature over `to_signable_string`, i.e., the body, so the shop header plays no role in the check: [3](#0-2) 

`Registry.process` validates the HMAC and then unconditionally forwards `request.shop` (the unauthenticated header) to the app handler as the tenant identity for the delivered payload: [4](#0-3) 

Because `(raw_body, hmac)` is a valid pair for *any* shop whose secret matches (all shops of a given app share the same `api_secret_key`), a party who owns/operates one shop that has this app installed can legitimately trigger a real webhook (e.g. `orders/create`) on their own store, capture the resulting `(raw_body, x-shopify-hmac-sha256)` pair, and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. The HMAC check still passes because it never inspected the shop header, and the handler receives `WebhookMetadata` claiming the payload came from the victim shop.

### Impact Explanation
This directly enables cross-tenant confusion: an app's webhook handler that keys per-shop side effects (e.g., updating billing state, order records, inventory sync, revoking access) off `WebhookMetadata#shop` can be made to apply attacker-controlled, HMAC-"verified" data to a different merchant's tenant record, since the "verification" never actually bound the claimed shop to the signed bytes.

### Likelihood Explanation
Requires only that the attacker be a legitimate installer of the public app on their own store (an unprivileged internet user, since apps are installable by any Shopify merchant) — no access to `api_secret_key`, access tokens, or the victim's credentials is needed. They only need to observe one webhook delivery to their own shop and replay it with a modified header, which any HTTP client can do since header/body binding is never enforced by this gem.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed material, or otherwise cryptographically or out-of-band bind the shop domain to the payload before trusting it in `Registry.process`. At minimum, cross-check `request.shop` against an expected/registered shop for the delivery (e.g., a shop the app knows it installed webhooks for) rather than trusting the header verbatim once body-HMAC succeeds.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a real webhook (e.g. creates an order), letting Shopify legitimately deliver it to the app's callback URL with a valid `x-shopify-hmac-sha256` computed over the JSON body using the app's shared `api_secret_key`.
2. Attacker captures the exact `raw_body` and `x-shopify-hmac-sha256` value from that delivery.
3. Attacker sends a new POST to the same webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` in [3](#0-2)  succeeds because it only recomputes HMAC over the unchanged body.
5. `Registry.process` in [4](#0-3)  builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and invokes the app's handler, which now processes attacker-controlled data as if it originated from the victim's store.

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
