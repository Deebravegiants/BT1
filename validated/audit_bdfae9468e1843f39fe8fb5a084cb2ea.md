## Title
Webhook `shop-domain` and `topic` Headers Are Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, while the `shop` and `topic` values used to route and label the payload are read from unauthenticated HTTP headers. This breaks the identity binding: **shop/topic acted upon ≠ shop/topic covered by the HMAC**.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` and `topic` are pulled from headers that are never included in the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` only re-computes the HMAC over `verifiable_query.to_signable_string` (the raw body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` accepts the request once that body-only HMAC check passes, then dispatches using the **unauthenticated** `request.topic` and hands `request.shop` straight to the handler as tenant identity: [4](#0-3) 

Because the app's `api_secret_key` is a single shared secret used to HMAC-sign webhooks for **every** shop installed on the app (multi-tenant), any merchant who installs the app on their own store receives a genuine webhook whose HMAC is valid for that raw body under the app's secret. That merchant can capture the raw body + valid HMAC from a webhook addressed to their own shop, then replay the identical body/HMAC pair to the app's webhook endpoint with a forged `x-shopify-shop-domain` (and/or `x-shopify-topic`) header pointing at a different shop. The HMAC check still passes (it only verifies the body bytes), and `WebhookMetadata` will carry an attacker-chosen `shop` value paired with the replayed body: [5](#0-4) 

This is the same bug class as the source report: a value the handler *acts on* (here, the shop identity used for tenant routing) is not bound by the same authenticator (HMAC) that verifies the payload it is attached to.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` to key session/store lookups or per-tenant data updates (the pattern this gem's docs recommend for identifying which merchant a webhook is for), an attacker who legitimately installs the app on their own store can inject data into another tenant's context — a cross-tenant access/confusion vulnerability. This matches the Critical severity bucket ("cross-tenant access").

### Likelihood Explanation
The attacker only needs to be an ordinary, low-privilege user of the multi-tenant app (install the app on a shop they control) — no access token, secret, or privileged account of the victim shop is required, satisfying the "unprivileged internet user" constraint. Capturing their own valid webhook body/HMAC and replaying it with different headers requires no cryptographic material beyond what Shopify already sends them.

### Recommendation
Include the `shop` and `topic` header values in the signable content that the HMAC verifies, or otherwise cryptographically bind them to the payload (e.g., require the handler to separately re-validate `shop` against a known/registered value before trusting it), so header spoofing cannot decouple the authenticated body from the routing metadata used by handlers.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`.
2. Shopify sends a legitimate webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and some JSON body.
3. Attacker captures the exact raw body and its valid HMAC.
4. Attacker (or a script under their control) POSTs the identical raw body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) validates the HMAC successfully (body unchanged) and invokes the handler with `shop: "victim-shop.myshopify.com"`, causing the app to process attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
