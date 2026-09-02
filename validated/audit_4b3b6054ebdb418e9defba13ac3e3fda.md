### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity used for dispatching a webhook (`shop`) from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that `Utils::HmacValidator` verifies covers only the raw request body. Because the `shop` value is never part of the bytes that are authenticated, an attacker who owns any shop where the host app is installed can take a legitimately-signed webhook payload and relabel it with a victim shop's domain; the signature still validates and the host app processes the payload as if it originated from the victim tenant.

### Finding Description
The binding that should hold is:

`HMAC_valid(bytes, client_secret) == true` ⟺ `(topic, shop, body)` as processed by the handler were all produced/authorized by Shopify for that `shop`.

In `Webhooks::Request`, `to_signable_string` returns only the raw body: [1](#0-0) 

while `shop` is read from an unauthenticated header: [2](#0-1) 

`Utils::HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` against the received HMAC using the app's shared secret: [3](#0-2) 

`Registry.process` uses the result of that validation as the sole gate before dispatching, and then trusts `request.shop` — the unauthenticated header — as the tenant for the handler call: [4](#0-3) 

Because the `client_secret` used to sign webhooks is shared across every shop that installs a given app (it is not per-shop), any tenant that legitimately installs the app receives correctly-HMAC-signed webhook deliveries for its own shop. Since `shop` is excluded from the signed bytes, an attacker who controls such a shop can capture one of these genuine `(body, hmac)` pairs and re-deliver it to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with any victim shop domain. `HmacValidator.validate` still returns `true` because it never inspected the header, and `Registry.process` hands the forged tenant identity straight to the app's registered handler as `WebhookMetadata#shop`.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook authenticity: the `shop` value handed to application webhook handlers is attacker-controlled even though the request passed HMAC "validation." Any host application that trusts `WebhookMetadata#shop` (as the library's own API implies it should) can be made to apply attacker-supplied topic/body data against a victim shop's records — e.g. triggering `app/uninstalled`-style cleanup, GDPR data-request handling, or data-sync logic keyed on the wrong shop. This is cross-tenant access/data confusion achieved purely by an unprivileged actor who has installed the app on a shop they control, satisfying the Critical "cross-tenant access" impact criterion.

### Likelihood Explanation
Likelihood is high given reachability: any user can install a public app, receive real webhook deliveries signed with the app's real (shared) `client_secret`, and replay the body with a modified shop-domain header to the app's webhook endpoint. No knowledge of `api_secret_key`, access tokens, or privileged access is required — only a normal app installation, which is the baseline unprivileged-attacker capability assumed by these rules.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook-id`) values in the signable bytes verified by `Utils::HmacValidator`, or otherwise cryptographically bind the header-derived tenant identity to the signed payload before it is exposed via `WebhookMetadata#shop`. At minimum, `Webhooks::Request#to_signable_string` should not be limited to the raw body alone when `shop` is later trusted as an authenticated identity for dispatch.

### Proof of Concept
1. Attacker installs the target public app on `attacker.myshopify.com`, causing Shopify to deliver a legitimate webhook, e.g.:
   ```
   Shopify-Topic: orders/create
   Shopify-Hmac-Sha256: <valid HMAC of raw_body with app client_secret>
   Shopify-Shop-Domain: attacker.myshopify.com
   Shopify-Webhook-Id: ...
   <raw_body>
   ```
2. Attacker replays the same request to the app's webhook endpoint, only changing the header:
   ```
   Shopify-Shop-Domain: victim.myshopify.com
   ```
   leaving `raw_body` and `Shopify-Hmac-Sha256` untouched.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only [5](#0-4)  and succeeds since the body is unchanged.
4. The handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop` now resolves to `"victim.myshopify.com"` [6](#0-5) , causing the host application to act on attacker-controlled data attributed to the victim's tenant.

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
