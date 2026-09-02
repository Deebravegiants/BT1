This confirms the finding. I have sufficient evidence to produce the analog.

### Title
Webhook `shop-domain` identity is not covered by the HMAC signature, enabling cross-tenant shop attribution - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The reported Unlock Protocol bug is a broken-binding exploit: the protocol authenticates one thing (a slow-updating oracle price) while acting on another (referrer UDT payouts tied to key purchase volume), letting an attacker decouple the "verified" value from the value actually used. The same class of bug exists in this gem's webhook processing: `ShopifyAPI::Utils::HmacValidator` cryptographically verifies only the raw request body, while `ShopifyAPI::Webhooks::Registry.process` hands the caller's unauthenticated `shop-domain` header straight through to the app as the tenant identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors instead read directly from caller-supplied HTTP headers with no cryptographic binding to the body: [2](#0-1) .

`HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`, i.e. the raw body: [3](#0-2) .

`Registry.process` checks only that this body-only HMAC is valid, then forwards `request.shop` (an unverified header) to the host application's handler as the trusted tenant identity: [4](#0-3) . `WebhookMetadata.shop` is a plain `String` field with no relationship to the signed bytes: [5](#0-4) .

The broken identity binding, stated as an equality that the gem fails to enforce:
`HMAC_valid(raw_body) == true` should imply `shop_header == shop_that_actually_owns(raw_body)`, but the gem only guarantees the former and lets the host trust the latter unchecked.

### Impact Explanation
Because the signature covers none of the identity headers, an attacker who owns any shop that installs the app can capture one of their own legitimately-signed webhook deliveries (valid `raw_body` + valid `hmac`) and replay the identical `raw_body`/HMAC pair to the same webhook endpoint while substituting an arbitrary victim `shop-domain` (and `topic`/`webhook_id`) header. `Registry.process` will pass HMAC validation (it only checks the body) and dispatch a `WebhookMetadata` claiming the victim shop as the source: [6](#0-5) . Any host application that uses `data.shop` to select which tenant's session/access token to load or which tenant's records to mutate (a documented, expected usage pattern per this gem's webhook design) will act on attacker-controlled data under a victim's identity — a cross-tenant access/data-integrity violation.

### Likelihood Explanation
The prerequisite is only that the attacker controls one shop with the app installed (an ordinary unprivileged merchant), which is normal, unprivileged access to any public app — no `api_secret_key`, access token, or leaked credential is required. Capturing one's own webhook body/HMAC and re-POSTing it with modified headers to the app's public webhook URL is straightforward for anyone who can install the app once.

### Recommendation
Include the identity-relevant fields (`shop-domain`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material, or otherwise cryptographically bind them to the body (e.g., verify the HMAC over a canonical string containing headers + body, or require the host application be told explicitly that these headers are unauthenticated and must be independently verified, e.g. by looking up the shop from a store already known to be tied to a valid installed session rather than trusting the header). At minimum, update `HmacValidator`/`Webhooks::Request` so `to_signable_string` incorporates the shop domain, and document clearly that `WebhookMetadata.shop` is not currently authenticated by the HMAC check.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers any webhook (e.g. `orders/create`), capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header — both are valid per `HmacValidator.validate`.
2. Attacker resends the exact same body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this successfully (all required headers present) and `HmacValidator.validate` returns `true` because it only hashes `raw_body`, per [3](#0-2)  and [1](#0-0) .
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-controlled JSON>, ...)`, per [7](#0-6) .
5. Any host application logic keyed on `data.shop` (e.g. "load victim's session/access token and process this order payload") now processes attacker-controlled data attributed to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
