### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant shop spoofing after a valid webhook is replayed - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook `Request` as fully authenticated once `Utils::HmacValidator.validate(request)` succeeds, and forwards `request.shop` (taken straight from the `X-Shopify-Shop-Domain` header) into the handler via `WebhookMetadata`. However, the HMAC only ever signs the raw request body — never the shop-domain, topic, webhook-id, or api-version headers. This breaks the intended identity binding `hmac(body) → shop`, letting anyone who can produce one genuine, HMAC-valid webhook body (e.g. from their own installed shop) attribute that body to an arbitrary different shop when replaying it to the app's webhook endpoint.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` are all read from HTTP headers with no cryptographic tie to the body or to each other: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC using `verifiable_query.to_signable_string`, i.e. the body only: [3](#0-2) 

`Registry.process` gates entirely on that body-only HMAC check, then immediately hands `request.shop` (unauthenticated) to the handler as if it were verified: [4](#0-3) 

The equality the library implicitly promises to callers is:
`HmacValidator.validate(request) == true` ⇒ `(request.shop, request.topic, request.body)` are all authentic and bound together.

In reality the equality that actually holds is only:
`HmacValidator.validate(request) == true` ⇒ `request.body` is authentic (produced with the app's `api_secret_key`).

`request.shop` is not part of the signed bytes, so it can be swapped for any value without invalidating the signature — the classic "bytes verified vs. bytes parsed/acted on" binding break called out in the report's bug class, applied here to the shop-domain field instead of the amount field.

### Impact Explanation
Any actor who can obtain one genuinely signed webhook body (trivially possible for an attacker who installs the app on their own store, or observes any legitimate webhook payload shape, since bodies for many topics — and especially generic/empty ones — are attacker-influenceable or predictable) can replay that exact `(body, hmac)` pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. `Registry.process` will accept it (HMAC over the body still matches) and dispatch it to the registered handler with `WebhookMetadata#shop` set to the victim's domain and `body` set to attacker-chosen content for that topic. If the consuming application uses `data.shop` to select which tenant's state to mutate (the overwhelmingly common pattern for webhook handlers — e.g. "update order/product data for shop X"), this results in cross-tenant data corruption/injection: an unprivileged internet user with no relationship to the victim shop can cause writes attributed to that shop using content they fully control. This satisfies the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Exploitation requires no access token, no `api_secret_key`, and no privileged account — only the ability to send an HTTP POST to the app's public webhook URL with attacker-chosen headers and a body+HMAC pair that was legitimately produced once (e.g. from the attacker's own store, which anyone can create for free on Shopify, or from any predictable/attacker-triggerable webhook body such as an empty `{}` payload for topics that don't require order/customer-specific content). This is a low-effort, purely network-level attack fully within an unprivileged internet user's capability.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the authenticated context instead of trusting the raw header value:
- Require callers to supply the expected/registered shop domain (from their own session/install record) and reject the webhook if it doesn't match `request.shop`, rather than treating `request.shop` as ground truth.
- Alternatively, include the shop-domain header value in `to_signable_string`/the HMAC computation if Shopify's platform is extended to support it, so the signature actually binds body↔shop.
- At minimum, document clearly in `WebhookMetadata`/`Registry.process` that `shop`, `topic`, and `webhook_id` are unauthenticated header values and must be cross-checked by the consuming app against its own installed-shop records before being used for any tenant-scoped action.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` (or otherwise obtains one legitimate webhook delivery), capturing a valid `(raw_body, X-Shopify-Hmac-Sha256)` pair, e.g. body `{}` with `hmac = HMAC-SHA256(api_secret_key, "{}")` as used in the test fixtures: [5](#0-4) 
2. Attacker sends a POST to the victim app's webhook endpoint with the same body and HMAC, but:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: <topic the app handles>`
3. `Registry.process` calls `HmacValidator.validate(request)`, which succeeds because it only checks the body: [6](#0-5) 
4. The registered handler executes with `WebhookMetadata.shop == "victim-shop.myshopify.com"` and attacker-controlled `body`, even though the victim shop never sent this webhook: [7](#0-6)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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

**File:** test/webhooks/registry_test.rb (L16-28)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }
```
