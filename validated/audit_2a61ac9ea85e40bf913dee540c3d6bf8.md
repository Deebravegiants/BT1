## Title
Webhook HMAC only signs the body, not the `shop-domain`/`topic`/`webhook-id` headers, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` verifies nothing but the body bytes. The `shop`, `topic`, `webhook_id`, and `api_version` values — all taken directly from unauthenticated HTTP headers — are never covered by the HMAC, yet `Webhooks::Registry.process` forwards them unchanged to the app's handler as the tenant identifier.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

and `hmac` is likewise pulled from the `hmac-sha256` header: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the raw body) and compares it against the `hmac` header: [3](#0-2) 

`Registry.process` trusts this validation and then passes `request.shop` (read straight from the `shop-domain` header, with no relationship to the signed bytes) into `WebhookMetadata` given to the app's handler: [4](#0-3) 

The equality that should hold is: `shop bound by HMAC == shop delivered to handler`. Instead, the HMAC only binds the body bytes, while `shop` (and `topic`, `webhook_id`, `api_version`) are unauthenticated header values that flow into the handler as the trusted tenant identifier — the exact "field acted on but not covered by the HMAC" pattern.

### Impact Explanation
Because `shop` is not cryptographically bound to the signature, an attacker who controls any shop with the app installed can capture one of their own genuine, validly-signed webhook deliveries (e.g., trigger an `orders/create` event in their own store) and replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `Registry.process` will still validate the HMAC (it only checks the body) and will hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop. Any host application that uses `data.shop` from the handler to select which tenant's data/session to update (the documented and expected usage pattern) will process attacker-controlled webhook data under the identity of a different merchant — a cross-tenant data-injection/confusion vulnerability.

### Likelihood Explanation
The attacker only needs to operate one shop that installs the target app (a normal, unprivileged merchant capability) and to be able to reach the app's public webhook endpoint, which is exposed with no additional authentication besides this HMAC check. No knowledge of `api_secret_key` is required — the attacker reuses a legitimately signed payload and only forges the unsigned header.

### Recommendation
Include the `shop` domain (and ideally `topic`/`webhook_id`) inside the signed material, or otherwise bind them cryptographically/contextually to the HMAC before trusting `request.shop` as the tenant identifier — e.g., verify the `shop-domain` header corresponds to a shop with a stored, valid session/installation for this app, independent of the raw-body HMAC.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a real event (e.g., creates an order), causing Shopify to POST a webhook with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac of body>`, and the JSON body.
2. Attacker captures this request, then resends it to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` and leaving body/HMAC untouched.
3. `Registry.process` (via `Utils::HmacValidator.validate`) validates successfully because it only checks the body against the HMAC: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, processing it as if it legitimately originated from the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
