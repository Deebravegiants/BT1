## Finding: Webhook `shop` attribution is not covered by the HMAC signature

### Title
Webhook shop identity is not bound to the HMAC signature, enabling cross-tenant webhook data confusion - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (and `topic`/`webhook_id`) values consumed by the registry are read straight from unauthenticated HTTP headers. `HmacValidator.validate` therefore proves that *some* valid body was signed by the app's secret, but it proves nothing about which shop that body belongs to, breaking the binding: `shop authenticated == shop the handler acts on`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`:
<cite repo="AYontt/shopify-api-ruby--003" path="lib/shopify_api/webhooks/request.rb" start="35="38" /> [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from request headers, none of which are part of the signed payload: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` (the raw body) against the HMAC header: [3](#0-2) 

`Registry.process` then trusts `request.shop` for routing/attribution after only verifying the body's HMAC: [4](#0-3) 

Because the shop identity is never part of the HMAC-signable string, the equality "HMAC-verified sender == shop attributed to this data" does not hold. Anyone who can obtain one legitimate `(raw_body, hmac)` pair generated with the app's `client_secret` — for example, by installing the app on their own store and capturing a webhook delivery for it — can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. `HmacValidator.validate` still returns `true` because the body and HMAC are genuinely valid, and `Registry.process` will hand the app's handler a `WebhookMetadata` whose `shop` is the attacker-chosen value: [5](#0-4) 

This is the same class of bug flagged in the external report: the field an application uses to make trust decisions (the deposit rate / here, the shop tenant) is not the field actually covered by the cryptographic guarantee (the signed amount / here, the signed body).

### Impact Explanation
If the host application uses `WebhookMetadata#shop` to key any tenant-scoped action (e.g. marking an app as uninstalled for a shop, updating shop-scoped billing/subscription state, or writing merchant records) without any other independent shop verification, an attacker who legitimately possesses one valid `(body, hmac)` pair (trivially obtainable by installing the app on any store they control) can cause that data to be attributed to a victim shop of their choosing. This is a cross-tenant data/state confusion issue that maps to the Critical "cross-tenant access" category.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on any store — something any developer/unprivileged user can normally do for a public app, and (2) POSTing the captured raw body/HMAC to the app's own public webhook endpoint with a forged `shopify-shop-domain` header. No access to the app's `client_secret`, access tokens, or TLS interception is required, satisfying the "unprivileged internet user" bar. The overall impact still depends on what the specific integrating app does with `data.shop`, since this gem's `Registry` is a thin dispatcher — but the missing binding is present in every consumer of this API purely by using the documented `Registry.process` flow.

### Recommendation
Include the shop domain (and ideally the topic/webhook id) in the signable string, or otherwise cryptographically bind the shop that is passed to the handler to the verified HMAC, e.g., by having `HmacValidator` verify a canonical string composed of `shop + topic + raw_body` rather than `raw_body` alone. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must be independently reconciled by the caller against a known/installed shop list before being trusted for tenant-scoped actions.

### Proof of Concept
1. Attacker installs the target Shopify app on their own development store `attacker.myshopify.com`, receiving legitimate webhook deliveries such as `orders/create` with a valid `x-shopify-hmac-sha256` header computed over the JSON body using the app's real `client_secret`.
2. Attacker captures one such `(raw_body, hmac)` pair.
3. Attacker sends a POST request directly to the app's public webhook endpoint with:
   - `x-shopify-hmac-sha256`: the captured valid HMAC
   - `x-shopify-topic`: `orders/create`
   - `x-shopify-shop-domain`: `victim-shop.myshopify.com` (forged)
   - body: the captured raw body
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the body against the HMAC. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to process the attacker's data as if it belongs to the victim shop.

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
