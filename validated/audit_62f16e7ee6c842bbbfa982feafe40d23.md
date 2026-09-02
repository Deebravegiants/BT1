### Title
Webhook shop identity is trusted from an HMAC-unsigned header, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` identity that the handler receives and acts on is taken from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never included in the signed content.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop` is read straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then immediately forwards `request.shop` (the unauthenticated header value) into `WebhookMetadata` for the app's handler to act on: [3](#0-2) 

`HmacValidator.validate` and `validate_signature` only ever hash `verifiable_query.to_signable_string` (the body), never the shop header, so a valid signature says nothing about which shop the request claims to be from: [4](#0-3) 

The identity binding that should hold is: `shop asserted in the HMAC-covered payload == shop the handler acts on`. Instead the gem enforces `hmac(raw_body) is valid` and separately trusts `shop = unsigned header`, so these two are not bound together. Any party that can obtain one genuine `(raw_body, hmac)` pair signed with the app's secret — for example a merchant who installs the app on their own shop and receives a real webhook — can replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a different (victim) shop's domain. `HmacValidator.validate` will still pass because it only checks the body bytes, and `Registry.process` will dispatch the payload to the app's handler tagged as belonging to the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to preserve for webhook processing: an unprivileged user who is a legitimate tenant of the app (i.e., installed it on their own store) can cause the host application to process arbitrary webhook payloads under another tenant's shop identity. Depending on how the host app's `WebhookHandler` uses `data.shop` (e.g., to look up/update per-shop records, write audit logs, or trigger shop-scoped side effects), this enables cross-tenant data corruption or disclosure — matching the "Critical: cross-tenant access" impact category, since the shop binding that the handler relies on for tenant isolation is not actually authenticated.

### Likelihood Explanation
Exploitability depends on the attacker being able to obtain at least one genuine `(raw_body, hmac)` pair — trivially achievable by any developer/merchant who installs the app themselves and captures one of their own real webhooks (bodies for many topics, e.g. `app/uninstalled`, `shop/update` with minimal/predictable fields, are easy to obtain or even trigger repeatedly). No access to the app's `client_secret` or any privileged credential is required, only normal use of the app as an unprivileged install. The main variable is whether the specific webhook topic's `raw_body` content is attacker-influenced/predictable enough to be useful against a target — this makes the likelihood topic-dependent but non-zero and realistic for many topics.

### Recommendation
Bind the shop identity into what's cryptographically verified: either include the shop domain in the HMAC-signed payload (not possible since the signature format is dictated by Shopify), or — since Shopify's webhook contract does not sign the shop header — the gem should document/require the host application not treat `shop`/`shop-domain` header as authenticated on its own, and where feasible cross-check the parsed body's own shop-identifying fields (e.g., domain-shape fields present in most webhook payloads) against the header before dispatch, or provide the raw body to the handler in a way that makes clear the header is unauthenticated. Alternatively/additionally, provide a strict per-shop webhook secret or shared-secret verification path so replay across shops cannot succeed even with a legitimate `(body, hmac)` pair for one shop.

### Proof of Concept
1. Attacker installs the target app onto their own store `attacker.myshopify.com` and receives (or triggers) a legitimate webhook, e.g. `app/uninstalled`, with body `B` and header `x-shopify-hmac-sha256: H` (valid for `B` under the app's secret).
2. Attacker POSTs to the app's webhook endpoint with the same raw body `B` and the same header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which hashes only `raw_body` (`B`) and compares to `H` — this succeeds because `B`/`H` is a genuinely valid pair. [5](#0-4) 
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` using `request.shop == "victim-shop.myshopify.com"` from the forged header, and invokes the app's handler with this spoofed shop identity. [6](#0-5) 
5. The host application's webhook handler processes `B` as if it originated from `victim-shop.myshopify.com`, even though `victim-shop` never sent this webhook — demonstrating the cross-tenant identity spoof.

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
