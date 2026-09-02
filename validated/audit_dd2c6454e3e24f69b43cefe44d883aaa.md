Confirmed root cause: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read directly from the unauthenticated `shopify-shop-domain` header [2](#0-1) . The HMAC check in `Registry.process` only validates `raw_body` against the secret and never binds it to the `shop` header before dispatching to the handler with that unauthenticated shop value [3](#0-2) .

### Title
Webhook `shop` identity not covered by HMAC allows cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
The gem's webhook verification computes the HMAC over the raw request body only, but the `shop` value used to attribute webhook data to a merchant is taken from the `X-Shopify-Shop-Domain`/`shopify-shop-domain` HTTP header, which is not included in the signed content. This breaks the binding `shop_verified == shop_used`.

### Finding Description
`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received HMAC [4](#0-3) . For webhooks, `to_signable_string` is defined as simply `@raw_body` [1](#0-0) , meaning the HMAC only authenticates the body bytes — none of the headers, including `shop`, are part of the signed data.

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` [5](#0-4)  and then immediately dispatches to the app's handler using `request.shop`, which is read straight from the header without any cryptographic binding to the HMAC-covered body [6](#0-5) , [2](#0-1) .

Because Shopify's real webhook HMAC (computed server-side with the app's `client_secret`) is also only calculated over the raw body (this is a Shopify platform behavior the gem simply mirrors), any entity that legitimately receives a webhook for one shop — e.g., an attacker who installs the app on their own store — obtains a `(raw_body, hmac)` pair that remains valid regardless of which `shop-domain` header accompanies it. The attacker can then replay that exact body+HMAC pair to the app's webhook endpoint while substituting an arbitrary victim `shop-domain` header value. `HmacValidator.validate` still succeeds (only body bytes are checked), and `Registry.process` passes the attacker-controlled `shop` value straight into `WebhookMetadata` for the handler to act on — attributing attacker-supplied data to a victim tenant.

### Impact Explanation
This crosses a tenant boundary: an app built on this gem cannot distinguish "the body Shopify signed" from "the shop the body is claimed to belong to," since the two are verified independently. A host application that stores/updates per-shop data keyed by `WebhookMetadata#shop` (the documented, gem-provided field) can be tricked into writing or acting on data under a different merchant's shop identifier, i.e., cross-tenant access/data corruption using only a webhook the attacker legitimately received for their own store.

### Likelihood Explanation
Requires only that the attacker operate one shop with the app installed (unprivileged, no `api_secret_key`/token needed) and be able to POST to the app's public webhook endpoint with modified headers. This is a realistic, low-effort attack path for any external, unauthenticated party who can install the app.

### Recommendation
Bind `shop` (and other routing-relevant fields like `topic`) into the HMAC-signed content in `to_signable_string`, or have `Registry.process`/host apps cross-check `request.shop` against a shop already known to be authorized for this specific webhook (e.g., verifying the shop associated with the webhook_id/subscription) rather than trusting the raw header value implicitly for identity attribution.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and receives a legitimate webhook: body `B` with header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's secret) and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker replays the same request to the app's webhook endpoint, keeping `B` and `H` unchanged but setting `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` recomputes the HMAC over `request.to_signable_string` (`== B`) and it matches `H`, so validation passes [7](#0-6) , [8](#0-7) .
4. `Registry.process` dispatches `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed_body_of_B, ...)` to the handler [9](#0-8) , letting the attacker inject data attributed to `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
