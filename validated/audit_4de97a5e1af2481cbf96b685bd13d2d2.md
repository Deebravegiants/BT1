## Title
Webhook shop-domain identity not bound to HMAC allows cross-tenant webhook spoofing — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic once the HMAC over the raw body validates, then hands the **unauthenticated** `shop` header straight to the app's handler. The HMAC only signs the request body, never the `X-Shopify-Shop-Domain` header, so the equality the app relies on — "the shop that signed this payload equals the shop reported in the header" — is never actually checked.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`request.shop` is read straight from the (attacker-controllable) HTTP header, independent of the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (i.e. body) against the shared `api_secret_key`, never touching `shop`: [3](#0-2) 

`Registry.process` then forwards the unverified `request.shop` value directly into `WebhookMetadata`, which is what the host application uses to determine *which tenant* the webhook belongs to: [4](#0-3) 

Because the Shopify app's `client_secret`/`api_secret_key` is shared across **every** shop that installs the app (it is not per-shop), any unprivileged internet user can install the same public app on their own (attacker-controlled) store, trigger a real webhook delivery to observe a genuine `(body, hmac)` pair, and then replay that exact body+HMAC directly to the app's public webhook endpoint while swapping the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header to a victim shop's domain. `HmacValidator.validate` still passes (the body/secret are legitimately matched), but `Registry.process` will invoke the handler with `shop: <victim-domain>`, letting the attacker inject fabricated webhook events (product/order/customer data, GDPR topics, etc.) attributed to a shop they do not control — a cross-tenant identity binding break, with no need for the app's `api_secret_key`, an access token, or any privileged credential.

### Impact Explanation
This breaks the tenant isolation the whole webhook flow is supposed to guarantee: `hmac-authenticated shop == request.shop`. An attacker can inject arbitrary attacker-controlled data into a victim shop's webhook processing pipeline (e.g. fake order/customer/GDPR webhooks), which can lead to state corruption, fraudulent business logic execution, or data poisoning scoped to a shop the attacker never installed the app on — this is a cross-tenant access vulnerability (Critical per the given impact tiers).

### Likelihood Explanation
Requires only (1) the app being a public/installable app (standard for any Shopify app using this gem's webhook flow), (2) the attacker installing it on their own store or otherwise obtaining one legitimate `(body, hmac)` webhook pair, and (3) sending a direct HTTP POST to the app's public webhook endpoint with a modified shop header — no secrets, tokens, or elevated access needed. This is straightforward for any unprivileged internet user.

### Recommendation
Bind the shop identity into the value that is HMAC/authentication-checked, e.g.:
- Require the host application to independently verify that `request.shop` corresponds to a shop with an existing, valid session/install record before trusting `WebhookMetadata#shop`, and document this requirement prominently, or
- Have `Registry.process` cross-check `request.shop` against an expected/registered shop list, or
- Include the shop domain in the signable string used for HMAC verification if/when Shopify's webhook contract allows it, so `HmacValidator.validate` fails whenever the shop header doesn't match the body's origin.

### Proof of Concept
1. Attacker installs the target public app on `attacker-shop.myshopify.com` (free/dev store, no special privilege required).
2. Attacker triggers any webhook topic they've subscribed to (e.g. `products/update`) and captures the raw POST body plus the `X-Shopify-Hmac-Sha256` header sent to their own registered endpoint — both are valid because they're really signed by Shopify with the app's shared secret.
3. Attacker sends this exact `(body, hmac)` pair directly to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds (body+secret match). `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) calls the app's handler with `shop: "victim-shop.myshopify.com"`, causing the app to process attacker-supplied data as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
