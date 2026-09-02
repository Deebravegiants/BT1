This confirms the vulnerability path.

### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant shop-identity spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify" before invoking the app's handler, but the HMAC check only authenticates the raw request body — not the `shop-domain` header that identifies which tenant the webhook belongs to. `WebhookHandler#handle` receives a `WebhookMetadata` struct whose `shop` field is taken directly from that unauthenticated header, so business logic keyed on `data.shop` trusts a value the signature never covered.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines `to_signable_string` to return only `@raw_body`: [1](#0-0) 
The `shop` accessor is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely independent of the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the body) and compares it to the received `hmac-sha256` header value: [3](#0-2) 

`Registry.process` only calls this HMAC validation, then passes the request's `shop` straight into `WebhookMetadata` for the handler: [4](#0-3) [5](#0-4) 

Because webhooks for every shop installed on an app are signed with the same app-level `api_secret_key` (Shopify's `client_secret`), a body/HMAC pair that is valid for one tenant is equally "valid" (HMAC-wise) for any other tenant serviced by the same app — the signature says nothing about which shop sent it. The binding that should hold is:
`shop authenticated (bound into the HMAC-covered bytes) == shop acted upon (data.shop passed to the handler)`
but the code instead enforces only:
`bytes verified (raw_body only) == bytes parsed (raw_body only)`,
leaving `shop` completely outside the equality. An attacker who controls a shop with the app installed (or who otherwise obtains one genuinely-signed webhook body+HMAC pair) can resubmit that same body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop that also has the app installed. `HmacValidator.validate` still returns `true` (it never inspects headers), and the handler executes with `WebhookMetadata#shop` set to the victim's domain — causing the app to attribute the attacker-controlled event/body to the victim tenant.

### Impact Explanation
This breaks the shop-authenticated vs. shop-acted-upon binding across tenants of the same app, which is a High severity issue under the cross-tenant-access criterion: an attacker can make the host application perform shop-specific side effects (e.g., data updates, redact/GDPR flows, entitlement or billing-state changes triggered by webhook topics such as `app/uninstalled`, `shop/redact`, `customers/redact`) against a shop they do not control, using only a webhook payload legitimately signed for their own shop. The library's documentation explicitly claims `process` "will verify the request did indeed come from Shopify," which overstates what is actually checked (body authenticity only, not sender/tenant identity), leading integrators to trust `data.shop` as authenticated when it is not.

### Likelihood Explanation
Exploitation requires only that the attacker control (or have previously observed) one genuinely Shopify-signed webhook body for an app that is also installed on the intended victim shop — a realistic scenario for any multi-tenant SaaS app on the Shopify App Store, since installing the app on a throwaway/dev shop is unprivileged and free, and `api_secret_key` is shared across all installs of the app.

### Recommendation
Bind the shop identity into the authenticated bytes, or otherwise independently verify it: include the `shop-domain` header value in `to_signable_string` (Shopify's own webhook signing already covers the body only, so the gem should additionally require callers/handlers to cross-check `data.shop` against a shop that is known to have a valid, previously-established session/installation for this specific `webhook_id`/topic before acting), and update `Utils::HmacValidator`/`Webhooks::Request` so that `process` cannot be mistaken for full sender-identity verification. At minimum, update the documentation in `docs/usage/webhooks.md` to clarify that `Registry.process` verifies payload integrity only, not which shop actually sent the request, and instruct integrators to validate `data.shop` against their own record of installed shops.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (self-service, no privilege required) and triggers any subscribed webhook topic, capturing the raw body `B` and the resulting `x-shopify-hmac-sha256` header `H` (computed by Shopify over `B` using the app's shared `api_secret_key`).
2. Attacker sends a POST to the app's webhook endpoint with the same raw body `B` and header `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and, if desired, `x-shopify-webhook-id`/`x-shopify-topic` to a topic of interest).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "x-shopify-shop-domain" => "victim-shop.myshopify.com", "x-shopify-hmac-sha256" => H})` is constructed.
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation succeeds.
5. The registered handler's `handle(data:)` is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, causing the app to perform shop-scoped logic against the victim tenant using attacker-supplied body content.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
