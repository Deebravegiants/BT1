## Finding

### Title
Webhook shop identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies its HMAC only over the raw request body, while the `shop` domain that is handed to the app's webhook handler is read from an unauthenticated HTTP header. This breaks the identity binding `shop authenticated == shop acted upon`: the HMAC proves the body wasn't tampered with, but it proves nothing about which shop the body belongs to.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is parsed straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `verifiable_query.to_signable_string` (i.e. the body) against `verifiable_query.hmac` (the `hmac-sha256` header) using `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` only calls this HMAC check, then immediately trusts `request.shop` and forwards it, unauthenticated, into `WebhookMetadata`, which the host app's handler will use to attribute the webhook to a tenant (e.g. to look up which shop's session/store row to update): [4](#0-3) 

`WebhookMetadata#shop` is a plain, unauthenticated `String`: [5](#0-4) 

Because the HMAC only binds the body bytes, two requests with the same body/hmac pair but different `shop-domain` headers both pass `HmacValidator.validate` and produce identical `hmac`/`body` but different `shop` in the resulting `WebhookMetadata`.

### Impact Explanation
This is a cross-tenant identity-binding break: `shop` (an authenticated-looking field consumed by the app) is not the field actually covered by the HMAC. An attacker who legitimately installs the app on a shop they control (an unprivileged internet user from the app's perspective — no `api_secret_key`, no access token, no privileged account required) can capture a real, validly-signed webhook delivery for their own shop (body + `hmac-sha256` pair, computed server-side by Shopify with the app's `api_secret_key`, which the attacker never needs to know), and replay that exact body/hmac pair to the same webhook endpoint while substituting a victim shop's domain in the `shop-domain` header. `Registry.process` will accept it (HMAC validates because the body is untouched) and dispatch it to the handler tagged as coming from the victim shop. Any host application that uses `WebhookMetadata#shop` to select which tenant's data to create/update/delete (a documented, intended use of this field) will act on the victim's tenant using attacker-supplied body content — i.e., cross-tenant data injection/corruption without needing any of the victim's credentials.

### Likelihood Explanation
Moderate. It requires the attacker to operate their own installation of the target app (trivial for a public app on the Shopify App Store) to obtain one legitimately signed webhook, then replay it at the shared public webhook endpoint with a forged `shop-domain` header — no cryptographic secret or privileged access is needed. The webhook endpoint is, by design, a public unauthenticated internet endpoint.

### Recommendation
Bind the shop identity into the verified signature domain, not just the body. Concretely: after HMAC validation, use `topic`/`body`-derived shop identifiers (or the recipient/registration configuration) instead of trusting the raw `shop-domain` header; or, at minimum, require handlers/consumers to independently validate that `data.shop` corresponds to a shop with an active installation/session before performing any tenant-scoped write, and document that `WebhookMetadata#shop` is not itself HMAC-covered so host apps don't treat it as authenticated.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` (their own store) and lets Shopify deliver a real webhook, e.g. `orders/create`, to the app's public webhook URL. They capture:
   - `raw_body` = `{"id":1,...}`
   - header `x-shopify-hmac-sha256` = `<valid HMAC over raw_body computed by Shopify using the app's api_secret_key>`
   - header `x-shopify-shop-domain` = `attacker.myshopify.com`
2. Attacker resends an HTTP POST to the same public webhook endpoint with the identical `raw_body` and identical `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only — it matches, so validation passes (`lib/shopify_api/utils/hmac_validator.rb` lines 12-31).
4. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...)` (`lib/shopify_api/webhooks/registry.rb` lines 188-199) and calls the app's handler, which processes attacker-controlled `body` under the identity of `victim.myshopify.com`.

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
