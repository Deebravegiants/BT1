### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the raw body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` value from the `x-shopify-shop-domain` HTTP header, but `Utils::HmacValidator` only authenticates the raw request body against that header. The `shop` field is never covered by the HMAC signature, so it can be swapped independently of the signed payload, breaking the binding `shop authenticated by HMAC == shop used as tenant identity`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight out of the `x-shopify-shop-domain` (or `shopify-shop-domain`) header, with no cryptographic tie to the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC purely from `verifiable_query.to_signable_string` (the body) and compares it to the `hmac` header value — it never incorporates `shop`: [3](#0-2) 

`Webhooks::Registry.process` validates the request with this HMAC check and then immediately hands `request.shop` (the unauthenticated header) to the app's handler as the tenant identity in `WebhookMetadata`: [4](#0-3) 

Because the shop is not part of the signed string, an attacker who obtains any single valid `(raw_body, hmac)` pair — e.g. by legitimately receiving a webhook for a shop/app installation they control — can replay that exact body and HMAC to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with an arbitrary victim shop domain. `HmacValidator.validate` will still succeed (it only checks the body bytes against the secret), and `Registry.process` will pass the victim shop identity plus the attacker-controlled body to the application's webhook handler as if Shopify itself reported that payload for that tenant. This is precisely the identity-binding gap described in the report's bug class: "a field acted on but not covered by the HMAC."

### Impact Explanation
This crosses a tenant boundary: an unprivileged actor (who only needs their own legitimate installation to harvest one valid signed webhook body) can make the library assert an arbitrary `shop` value paired with attacker-chosen webhook data. Any host application that uses `WebhookMetadata#shop` from this gem as the tenant key (a documented usage pattern) will process/store attacker data under another merchant's identity — i.e., cross-tenant data confusion/injection, without needing the app's `client_secret`, an access token, or any leaked credential.

### Likelihood Explanation
Requires the attacker to have received (not forged) at least one genuine webhook body+HMAC pair, which is trivial if the attacker runs their own shop and installs the target app (a normal, unprivileged action), then simply modifies the shop header when replaying the captured request to the app's public webhook endpoint.

### Recommendation
Bind `shop` (and ideally `topic`, `api_version`, `webhook_id`) into the signed material verified against the HMAC, or otherwise require the host application to independently authenticate/authorize the shop domain against the recipient shop separately from the HMAC check — do not treat the unauthenticated header value as trusted tenant identity once HMAC validation passes only on the body.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and registers a webhook subscription (e.g. `orders/create`).
2. Shopify delivers a webhook to the app: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's `client_secret`), header `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker replays the exact same `B` and `H` to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13`) recomputes HMAC over `B` only, matches `H`, and returns `true`.
5. `Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) proceeds and invokes the app's handler with `shop: "victim.myshopify.com"` and the attacker-controlled body `B`, despite the payload never having originated from or being validated against `victim.myshopify.com`.

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
