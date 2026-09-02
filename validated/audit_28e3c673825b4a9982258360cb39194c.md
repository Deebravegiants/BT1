## Finding [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook `shop` and `topic` fields are not covered by the HMAC signature, allowing cross-tenant/cross-topic webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `topic` and `shop` are read directly from HTTP headers without being part of the signed data. `Registry.process` trusts these unauthenticated header values to route and identify the tenant/topic once the body-only HMAC check passes.

### Finding Description
`Webhooks::Request` exposes `topic`, `shop`, `api_version`, and `webhook_id` purely as unauthenticated header reads: [4](#0-3) 

`to_signable_string` (the data actually covered by the HMAC) is only `@raw_body`: [5](#0-4) 

`HmacValidator.validate` computes/verifies the signature purely against `to_signable_string`: [6](#0-5) 

`Registry.process` accepts any request whose body-only HMAC checks out, then dispatches using the unauthenticated `topic` and `shop`: [2](#0-1) 

The intended identity binding should be: `hmac_valid(body, headers) == true` ⟺ `(shop, topic)` claimed in the headers are authentic. In the actual implementation, `hmac_valid` only proves `HMAC(api_secret_key, raw_body)` is correct — it says nothing about which shop or topic the payload was meant for. Because `api_secret_key` is one shared secret used for **every** shop installation of the app, any user who can trigger a legitimate webhook to their own store (a completely normal, unprivileged action — install the app, perform an action that fires a webhook) obtains a valid `(body, hmac)` pair. They can then replay that exact body+hmac to the app's webhook endpoint while substituting the `shop-domain` and/or `topic` headers (e.g. to a `shop/redact` or `customers/data_request` mandatory topic, or to another merchant's shop domain), and `Registry.process` will accept it and hand it to the corresponding handler as if it genuinely originated from that shop/topic.

### Impact Explanation
This breaks the tenant/topic identity binding that webhook consumers rely on. A host application using `WebhookMetadata#shop` / `#topic` to key per-tenant data operations (e.g. GDPR redaction handlers, subscription state changes) can be made to act on a different shop's identity than the one that actually produced the payload — a cross-tenant condition, since the same signing secret is shared by all shops of the app.

### Likelihood Explanation
Any actor who can install the app on a shop they control (i.e. any unprivileged internet user who becomes a merchant) can generate a valid webhook body+HMAC and then freely forge the `shop-domain`/`topic` headers when replaying it to the app's public webhook endpoint, since the gem's HMAC check never inspects those headers.

### Recommendation
Bind `shop` and `topic` (and ideally `webhook_id`, `api_version`) into the value that is HMAC-verified, or otherwise cryptographically tie the header claims to the signed body before they are used to key handler dispatch/tenant identification in `Registry.process`.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com` and receive any real webhook, capturing `raw_body = B` and the resulting `x-shopify-hmac-sha256` header value `H` (valid because `HMAC(secret, B) == H`).
2. Send a POST to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim-shop.myshopify.com` and `x-shopify-topic: shop/redact`.
3. `Utils::HmacValidator.validate(request)` succeeds because only `B` is hashed.
4. `Registry.process` looks up the handler for `shop/redact` and invokes it with `shop: "victim-shop.myshopify.com"`, even though the payload never came from Shopify for that shop/topic.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
