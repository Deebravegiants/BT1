## Title
Webhook `shop` identity is taken from an unauthenticated HTTP header while the HMAC only signs the request body — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the **raw body**, then trusts the `shop` value pulled from the `x-shopify-shop-domain` HTTP header — a field the HMAC never covers — to decide which tenant the event belongs to.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the `shop-domain`/`x-shopify-shop-domain` header, independent of the signed content: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC using `verifiable_query.to_signable_string`, i.e. body bytes only: [3](#0-2) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)`, then dispatches the handler using the *unauthenticated* `request.shop`: [4](#0-3) 

The identity binding the code implicitly assumes is:
`shop authenticated by HMAC == shop used to route/act on the webhook`

But in reality: `shop authenticated by HMAC` proves only "this exact body byte-string was HMAC-signed with `api_secret_key`" — it says nothing about which shop domain the event is for, since `shop-domain` is a plain header, not part of `to_signable_string`. This is the same class of bug as the referenced report: a field the code trusts and acts on (here, the shop that owns/receives the event) is not covered by the cryptographic check that is supposed to authenticate the request.

This differs from the OAuth callback path, where `AuthQuery#to_signable_string` does include `shop` in the signed params, so that flow is *not* vulnerable: [5](#0-4) 

### Impact Explanation
Any party who can obtain one validly-HMAC-signed webhook body (e.g., because they run their own shop installed on the same app, or because they capture a legitimate webhook delivery) can replay that exact body to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header for a different, victim shop. `HmacValidator.validate` still succeeds (it never looks at the header), and `Registry.process` calls the app's handler with `WebhookMetadata` claiming the event is `shop: <victim-shop>`. Any host application that uses `request.shop` (or the `shop` field of `WebhookMetadata`) to select the tenant's session/database record — the intended and documented use, per `handler.handle(data: WebhookMetadata.new(topic: ..., shop: request.shop, ...))` — will act on data for the wrong tenant. This is a cross-tenant integrity/isolation break attributable to this gem's own verification logic, not merely "the host app ignored guidance."

### Likelihood Explanation
The attack requires no secrets belonging to the victim and no special network position: replaying an HTTP POST with a modified header is trivial once one valid signed payload is obtained (e.g., from the attacker's own shop instance of the same app, which they legitimately control). Because the vulnerable code path (`Registry.process` / `HmacValidator.validate`) is the exact mechanism recommended in this gem's webhook documentation, essentially every consumer of `ShopifyAPI::Webhooks::Registry.process` is exposed.

### Recommendation
Bind the authenticated `shop` to the verification step, not just the header used downstream. Options:
- Include the `shop-domain` header value in the signable string used for the HMAC comparison (Shopify does not sign it today, so this alone can't be "fixed" purely client-side), or
- At minimum, require API consumers/callers to cross-check `request.shop` against the shop associated with any session/tenant lookup made afterward, and document/enforce that `shop` from `Webhooks::Request` must not be trusted as an authenticated value on its own; add a guard in `Registry.process` that only proceeds if the caller supplies (and the code validates) an expected shop for the currently-processing tenant context, rejecting mismatches.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a shop they control) and triggers a webhook event, capturing the raw POST: body `B`, headers include `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's real secret) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical request to the app's webhook endpoint, only changing `x-shopify-shop-domain` to `victim-shop.myshopify.com`, keeping body `B` and `x-shopify-hmac-sha256: H` unchanged.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`= B`) — this matches `H`, so validation passes: [6](#0-5) 
4. The handler is invoked with `WebhookMetadata` reporting `shop: "victim-shop.myshopify.com"` and body `B`, even though `B` was generated for the attacker's own shop, letting the attacker inject/forge tenant-attributed events for a shop they do not control.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
