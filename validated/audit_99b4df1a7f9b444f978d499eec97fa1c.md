This confirms the vulnerability. The test setup at `test/webhooks/registry_test.rb:16-30` shows the HMAC is computed only over the raw body `"{}"`, while `x-shopify-shop-domain` and `x-shopify-topic` headers are set independently and never included in the signed bytes.### Title
Webhook `shop` and `topic` identity fields are trusted from unauthenticated headers while the HMAC only covers the raw body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over `@raw_body`, but exposes `shop`, `topic`, `webhook_id`, and `api_version` as plain header reads that are never included in the signed bytes. `Registry.process` validates the HMAC and then immediately trusts `request.shop`/`request.topic` to dispatch the webhook and build `WebhookMetadata`, without any binding between the verified bytes and the tenant identity used downstream.

### Finding Description
`Utils::HmacValidator.validate` computes the expected signature from `verifiable_query.to_signable_string` and compares it to the `hmac` field [1](#0-0) . For webhooks, `Request#to_signable_string` returns only the raw request body, and `Request#hmac` decodes the `hmac-sha256` header [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors are read straight from HTTP headers with no cryptographic linkage to the signed body [3](#0-2) .

`Registry.process` validates only the HMAC (i.e., only proves the body bytes are authentic) and then uses `request.shop` and `request.topic` — fields outside the signed data — to route the webhook and construct the tenant-identifying `WebhookMetadata` passed to the app's handler [4](#0-3) .

This is the same identity-binding break as the referenced Volt bug: an attacker checks one thing (HMAC over body) but the code acts on another thing (shop identity from headers) that isn't covered by that check. The equality broken is: `bytes verified by HMAC == bytes the tenant identity is derived from`. Here, `bytes verified` = `raw_body` only, while `bytes identity is derived from` = `shop-domain header` (and `topic` header), which are disjoint.

The test fixtures confirm this construction directly: the HMAC is computed only over the JSON body `"{}"`, while `x-shopify-shop-domain` and `x-shopify-topic` are set independently in the same headers hash and never enter the signed string [5](#0-4) .

### Impact Explanation
If an unprivileged party can obtain one valid (body, HMAC) pair originally sent by Shopify to the app's webhook endpoint (webhook HMACs and bodies are not treated as secret by Shopify's own delivery model — they can be observed in transit, in logs, in retries, or replayed to the same publicly reachable endpoint), they can replay that exact body/HMAC combination while substituting an arbitrary `x-shopify-shop-domain` header. `Registry.process` will pass HMAC validation (since the body is unchanged) and will invoke the app's handler with attacker-chosen `shop` in `WebhookMetadata`, causing the host application to process/attribute webhook data under an arbitrary tenant identity of the attacker's choosing. This is a cross-tenant identity confusion at the point where this gem hands verified-but-mis-bound data to the app.

### Likelihood Explanation
Requires the attacker to have visibility into a single legitimate raw_body+HMAC webhook delivery for their own shop (which they legitimately receive, since they can request webhooks be created on their own store) and then replay it against the same public webhook endpoint with a different `shop-domain` header. No `api_secret_key` or privileged credential is required — the HMAC itself is provided in the same request the attacker controls the replay of. This is squarely an unprivileged-internet-user path.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string (or otherwise cryptographically bind them, e.g. append them to the HMAC input) so that any tampering with these header-derived identity fields invalidates the signature, mirroring the OAuth `AuthQuery#to_signable_string` pattern that binds `shop` into the signed payload [6](#0-5) .

### Proof of Concept
1. App registers a webhook and receives a legitimate delivery: `raw_body = "{}"`, header `x-shopify-shop-domain: victim-or-own-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over "{}">`.
2. Attacker captures/replays this exact `raw_body` and `hmac` header (unchanged) to the app's public webhook endpoint, but sets `x-shopify-shop-domain: attacker-shop.myshopify.com` (or any other target shop domain string).
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a request whose `hmac` still validates because `to_signable_string` only returns `raw_body` [7](#0-6) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)` — passes — then calls `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` using the attacker-controlled `shop` value [4](#0-3) .
5. The app's webhook handler processes/updates data keyed to the attacker-chosen `shop`, which is a cross-tenant identity confusion enabled purely by this gem's failure to bind the `shop` header into the HMAC-verified bytes.

Note: I could not locate a `WebhookMetadata` class file in the indexed portion of the repo (only its usage in `registry.rb`), so I cannot fully confirm every downstream consumer of `WebhookMetadata#shop`; this may be excluded from the current index due to size limits. The core finding — HMAC covering only body while `shop`/`topic` are read from unauthenticated headers and passed downstream in `Registry.process` — is fully confirmed from `lib/shopify_api/webhooks/request.rb` and `lib/shopify_api/webhooks/registry.rb`.

### Citations

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

**File:** test/webhooks/registry_test.rb (L16-30)
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

        @webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: @headers)
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
