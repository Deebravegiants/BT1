### Title
Webhook shop identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the `shop` (and `topic`) fields that are handed to the app's webhook handler come from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC of the body but never binds that signature to the shop the payload is attributed to, so an attacker who can obtain one genuinely-signed webhook (e.g., by installing the app on their own shop) can replay that exact body/HMAC pair while forging the `shop-domain` header to impersonate a different tenant.

### Finding Description
`to_signable_string` for a webhook request returns only the raw body: [1](#0-0) 

The `shop` and `topic` accessors, however, are read straight from HTTP headers that are not part of that signable string: [2](#0-1) 

`Registry.process` validates the HMAC of the request (i.e., of the body bytes only) and then dispatches to the handler using the *header-derived*, HMAC-unbound `request.shop` and `request.topic`: [3](#0-2) 

Because the webhook HMAC secret (`Context.api_secret_key`) is the app's single `client_secret`, shared across every shop that has the app installed, a valid HMAC only proves "this body was signed by Shopify using this app's secret" — it proves nothing about which shop the body belongs to. The binding the code implicitly relies on is:

`hmac_valid(body) == (shop_header authentic for that body)`

but the actual invariant enforced is only `hmac_valid(body)`; `shop_header` is never checked against anything derived from the signature. This is exactly the "field acted on but not covered by the HMAC" pattern: the shop identity used for tenant attribution downstream is disjoint from the data that was actually authenticated.

### Impact Explanation
Any shop owner that installs the app is a legitimate, unprivileged recipient of real, validly-signed webhooks for their own shop. That party can capture one such `(raw_body, hmac)` pair and re-POST it to the app's webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header pointing at a victim shop that also uses the app. `Utils::HmacValidator.validate(request)` will pass (the body/HMAC pair is genuinely valid for the shared secret), and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop. Any app that uses this `shop` field to select which tenant's data/session to update (a documented, expected usage of `WebhookMetadata`) will apply the replayed payload to the wrong tenant — a cross-tenant data-integrity/confusion issue reachable by any unprivileged app installer.

### Likelihood Explanation
Exploitation only requires installing the target app on any shop (which is the normal, unprivileged way third-party apps are used) and capturing one webhook delivery — no access to `api_secret_key`, access tokens, or any other credential is needed. The header manipulation itself is trivial (any HTTP client), and the gem performs no cross-check between the signed bytes and the `shop-domain` header before handing data to the app.

### Recommendation
Bind the shop identity to the authenticated payload instead of trusting the header independently: include the `shop-domain` (and ideally `topic`) header in the HMAC-signable string used by `to_signable_string`, or otherwise require host applications to independently verify that `request.shop` matches an installation that is expected to be receiving that specific signed body (e.g., cross-check against the shop stored for the corresponding webhook subscription). At minimum, document prominently that `request.shop`/`WebhookMetadata#shop` is not covered by the HMAC and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; Shopify delivers a real webhook with headers `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-hmac-sha256: <valid_hmac_of_body>`, and some `raw_body`.
2. Attacker captures `raw_body` and `shopify-hmac-sha256` from that delivery.
3. Attacker POSTs the same `raw_body` to the app's webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com` (keeping the same, still-valid HMAC header, since HMAC is computed over `raw_body` alone):
   ```ruby
   headers = {
     "shopify-topic" => "orders/create",
     "shopify-hmac-sha256" => captured_hmac, # valid for raw_body
     "shopify-shop-domain" => "victim-shop.myshopify.com", # forged
   }
   request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_raw_body, headers: headers)
   ShopifyAPI::Webhooks::Registry.process(request) # HMAC check passes; handler runs with shop = "victim-shop.myshopify.com"
   ```
4. `Utils::HmacValidator.validate(request)` returns `true` (see [4](#0-3) ), and the handler receives `WebhookMetadata` attributing the payload to `victim-shop.myshopify.com`, even though that shop never sent or received this webhook.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
