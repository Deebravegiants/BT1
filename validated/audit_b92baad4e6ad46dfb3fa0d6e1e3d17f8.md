### Title
Webhook shop-tenant spoofing via HMAC that only covers the raw body, not the `X-Shopify-Shop-Domain` header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
The external report's root cause is that a value used by the app (Balancer's `getAmountsOut`) doesn't invoke the verification it's supposed to. The closest reachable analog in this gem is an identity-binding gap: `ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while the `shop` (tenant) value taken from the `X-Shopify-Shop-Domain` / `shopify-shop-domain` header is never included in the HMAC-covered material, yet `Registry.process` trusts that header value as the tenant identity passed to the app's webhook handler.

### Finding Description
`ShopifyAPI::Webhooks::Request` computes the signable string exclusively from `@raw_body`: [1](#0-0) 

`shop` is read straight from an HTTP header with no cryptographic binding to the body: [2](#0-1) 

`Registry.process` validates only the HMAC (i.e., body integrity) via `HmacValidator.validate`, then immediately trusts `request.shop` as the tenant identity and forwards it to the handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only ever hash `verifiable_query.to_signable_string`, so for a `Webhooks::Request` object that string is the body alone — the `shop` field is never part of what's verified: [4](#0-3) 

Because the app-level `api_secret_key` used to compute the HMAC is shared across every merchant install of the app (it is not per-shop), any unprivileged user can install the app on their own store, receive a genuine webhook with a body they influence (or fully control fields of) and its correctly computed HMAC, and then replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header pointing at a victim shop. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` hands the handler a `WebhookMetadata` claiming to be from the victim shop: [5](#0-4) 

The binding that should hold is: `shop-identity used by handler == shop-identity actually authenticated by the signature`. Before the request, both are equal because Shopify itself sends the real header alongside the real body. After the attacker's replay, the header claims shop B while the only thing cryptographically verified (the body) originated from shop A's own install — the equality is broken, and the app's handler processes event data under shop B's identity.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who is merely a legitimate/unprivileged user of the app (via their own store installation) can cause the host application to execute webhook-handling logic (state updates, data writes, notifications, uninstall/reinstall side effects, etc.) attributed to a shop they do not own. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to key database records or trigger per-tenant side effects), this can lead to cross-tenant data corruption or unauthorized actions being taken against another merchant's tenant record — matching the "Critical – cross-tenant access" impact class.

### Likelihood Explanation
Exploitability requires: (1) the attacker to have a working install of the app (an ordinary, unprivileged action any developer/merchant can perform), (2) knowledge of a valid `(raw_body, hmac)` pair (trivially obtained from their own store's real webhook traffic, or by controlling fields of a webhook payload they can trigger, e.g. creating their own orders/products), and (3) the ability to POST to the app's public webhook endpoint with a forged shop-domain header — no secrets, tokens, or privileged access are required. This does not depend on any documented misuse by the host app; the gem's own `Request`/`Registry` code performs no binding between the verified bytes and the trusted `shop` value.

### Recommendation
- Short term: Have `Webhooks::Request#to_signable_string` (or `Registry.process`) include the shop domain (and ideally webhook id / topic) in the material that's cryptographically bound, or otherwise reject/flag requests where the header-provided shop cannot be correlated with a known, previously-established install/session record before invoking the handler.
- Long term: Add unit tests asserting that a valid-HMAC body replayed with a different `shop` header is rejected, so the shop claim is provably bound to the verified request, not just the JSON payload.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (a legitimate, unprivileged install flow) and triggers any webhook event (e.g., `orders/create`), capturing the raw POST body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (computed by Shopify using the app's shared `api_secret_key`).
2. Attacker replays: `POST /webhooks` with headers `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: victim-shop.myshopify.com`, and body `B` unchanged.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which hashes only `B` and matches `H` — validation passes. [6](#0-5) 
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, so the host app processes an event as if it came from `victim-shop`, despite it never having sent it. [5](#0-4)

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
