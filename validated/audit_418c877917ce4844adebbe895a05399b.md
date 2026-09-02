### Title
Webhook `shop-domain` header is trusted for tenant attribution but is not covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC that `HmacValidator.validate` checks binds nothing but the JSON payload. The `shop-domain` header — which is later exposed as `data.shop` to the host application's webhook handler and used to attribute the event to a tenant — is read straight from an attacker-controllable HTTP header and is never part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts `shop`, `topic`, `webhook_id`, and `api_version` purely from headers: [1](#0-0) 

But the signable string used for HMAC verification is only the raw body: [2](#0-1) 

`Registry.process` validates the HMAC and then hands `request.shop` straight to the app's handler as the tenant identifier, without any additional binding to the signed content: [3](#0-2) 

`HmacValidator` computes the HMAC purely over `verifiable_query.to_signable_string` (the raw body, in the webhook case) against `Context.api_secret_key`: [4](#0-3) 

Because the `api_secret_key` is a single per-app secret shared across every merchant that installs the app (not per-shop), any merchant who has installed the app can legitimately receive a correctly-signed webhook for their own shop. Since the shop header is outside the HMAC's scope, that same attacker can resend the identical `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `Utils::HmacValidator.validate` will still return `true` because it only ever re-computes the HMAC over the untouched raw body — the equality it actually checks is:

`HMAC(secret, raw_body) == received_hmac`

but the value the application *acts on* for tenant selection is `request.shop`, which is not part of that equality at all. The binding that should hold — `authenticated_shop == attributed_shop` — is broken.

### Impact Explanation
Any app that uses `data.shop` from `WebhookMetadata` (as the documented handler contract explicitly instructs, see `docs/usage/webhooks.md`) to select which tenant's session/data record to update, enqueue a job for, or invalidate cache for is vulnerable to cross-tenant event injection: a malicious merchant who installed the app can cause the app to process attacker-supplied webhook payloads under a victim merchant's identity. This is a cross-tenant integrity/confusion issue directly reachable by an unprivileged internet user who has done nothing more than install the app on their own store (no `api_secret_key`, access token, or victim credentials required).

### Likelihood Explanation
Any developer following the gem's own documented webhook handler pattern (`data.shop`) is exposed. The attacker only needs their own legitimate app installation to obtain one valid `(body, hmac)` pair, then a single forged HTTP request with a different `shop-domain` header value — no cryptographic secret is needed to exploit this once a legitimate pair is observed.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) in the signed material that `to_signable_string` returns for `Webhooks::Request`, or otherwise cryptographically bind the claimed shop to the signature before exposing it to `WebhookMetadata`, so that `HmacValidator.validate` fails if the shop header is altered independently of the body.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, receiving a legitimate webhook:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, body `{"id":1}`.
2. Attacker resends the exact same body and HMAC to the app's webhook endpoint, replacing only the header:
   - `x-shopify-shop-domain: victim.myshopify.com`
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, "{\"id\":1}")` and finds it matches the (unchanged) `hmac` header — validation succeeds: [5](#0-4) 
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: {"id"=>1}, ...)` and performs tenant-scoped processing (e.g., job enqueue, DB update) against the victim's tenant using attacker-controlled data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
