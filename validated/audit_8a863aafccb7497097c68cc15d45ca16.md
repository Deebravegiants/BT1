### Title
Webhook Shop-Domain Header Is Not Covered by HMAC, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request **body**. The `shop` identity that the gem hands to the host application's handler is read from the `shopify-shop-domain` header, which is never included in the HMAC-signed payload. Any actor who possesses one valid `(body, hmac)` pair for the shared app secret can attach an arbitrary `shop` value and have it accepted as authentic, breaking the binding between "HMAC-authenticated bytes" and "shop identity acted upon."

### Finding Description
`Request#to_signable_string` only returns the raw body: [1](#0-0) 

`HmacValidator.validate`/`validate_signature` compute and compare the HMAC exclusively over that signable string (the body) using the app-wide `Context.api_secret_key`: [2](#0-1) 

`Registry.process` treats HMAC success as full authentication of the request, then forwards `request.shop` — parsed straight from the (unsigned) `shopify-shop-domain` header — to the handler as the tenant identity: [3](#0-2) [4](#0-3) [5](#0-4) 

The `api_secret_key` (and thus the HMAC) is shared across **all shops** using a given app — it is not per-shop. Since `shop` (and `topic`, `webhook-id`, `api-version`) are headers that are never mixed into `to_signable_string`, the equality the gem actually verifies is:

`HMAC(body, api_secret_key) == received_hmac`

but the equality the host application is implicitly relying on (via `WebhookMetadata#shop`) is:

`shop header == tenant that produced this signed body`

These two are not the same binding. Any request whose body+HMAC pair is valid for the app (e.g., replayed from the attacker's own shop's legitimately-received webhook, or any other webhook the attacker can observe for the same app) will pass `Registry.process`'s only authentication check regardless of what `shop` domain is asserted in the header, because `shop` is parsed but never cryptographically bound to the signature.

### Impact Explanation
This breaks tenant isolation (cross-tenant access) in exactly the pattern called out in scope: "a field acted on but not covered by the HMAC." A merchant/attacker who has installed the app (and thus can generate at least one legitimately-signed webhook body for their own shop, e.g. by triggering `orders/create`) can replay that body to the app's webhook endpoint with a forged `x-shopify-shop-domain` header naming a victim shop. `Registry.process` will accept it as authentic and dispatch it to the handler tagged as belonging to the victim shop, letting the attacker inject data/events attributed to another tenant.

### Likelihood Explanation
The attacker only needs: (1) their own instance of the app installed on any shop (to legitimately receive at least one signed body/HMAC pair), and (2) the ability to POST to the app's public webhook endpoint with custom headers — both trivially available to any unprivileged internet user/merchant, with no access token, `api_secret_key`, or privileged access required.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed payload verification, or independently verify `shop` against Shopify's known/registered shops for the app before trusting it (e.g., cross-check against an installed-shop record) rather than trusting the unauthenticated header value used only for handler dispatch.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; trigger any webhook (e.g. `orders/create`) to capture a legitimate raw body `B` and its valid `x-shopify-hmac-sha256` header `H` (computed only over `B` with the shared `api_secret_key`).
2. POST to the app's webhook endpoint with:
   - `x-shopify-hmac-sha256: H`
   - `x-shopify-topic: orders/create`
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - body: `B`
3. `HmacValidator.validate` succeeds because it only checks `B`/`H` against `Context.api_secret_key`, per [6](#0-5) .
4. `Registry.process` dispatches the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, per [7](#0-6) , causing the host app to process attacker-controlled data as if it belongs to the victim tenant.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
