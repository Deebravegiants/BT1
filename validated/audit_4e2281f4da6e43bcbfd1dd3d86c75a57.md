### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value used by the webhook handler exclusively from the `x-shopify-shop-domain` (or `shopify-shop-domain`) HTTP header, while the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw request body. Because the tenant-identifying header is never included in the signed bytes, an attacker who legitimately controls one shop that has the app installed can take a validly-signed webhook payload and re-send it with a different `shop-domain` header, and the signature will still validate — even though the `shop` value consumed by the handler no longer matches the bytes that were actually verified.

### Finding Description
`Request#hmac` reads `x-shopify-hmac-sha256` and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shop-domain` header and is not part of the signed content: [2](#0-1) 

`Registry.process` validates the HMAC using this same `to_signable_string` (raw body only) and then trusts `request.shop` to build `WebhookMetadata` that is handed to the application's webhook handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`, i.e. the raw body, using the app's single `api_secret_key`: [4](#0-3) 

The test suite confirms this: the HMAC is computed only over the JSON body `"{}"`, while `x-shopify-shop-domain` is set independently in the headers hash and never enters the HMAC computation: [5](#0-4) 

**Identity binding broken (equality that should hold but doesn't):**
`bytes-verified-by-HMAC (raw_body)` should determine `shop-value-trusted-by-handler (request.shop)`, but instead `shop` is taken from an unauthenticated header that is disjoint from the signed bytes. Since the app's `api_secret_key` is shared across every shop that installs the app (it is not per-shop), any shop that has legitimately installed the app can compute a valid HMAC for an arbitrary body of its choosing (via its own genuine webhook deliveries, or via any endpoint that echoes attacker-controlled data through a real webhook), then replay that (body, hmac) pair with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `Utils::HmacValidator.validate` will report the request as valid because it only checks the body against the shared secret, and `Registry.process` will invoke the merchant's webhook handler with `shop: <victim-domain>` and attacker-chosen body content, causing the host application to process attacker data as if it were an authenticated event for the victim tenant.

### Impact Explanation
This is a cross-tenant access primitive: an unprivileged user who merely has (or can obtain) a working install of the app on their own store can forge webhook deliveries that appear to originate from a different merchant's shop, with attacker-controlled body content. Any host application that uses `WebhookMetadata#shop` to select which tenant's data/session to update (a documented and expected pattern, since `Registry.process` passes this value straight from the request to the handler) will write/act on data keyed to the wrong (victim) shop. This satisfies the Critical bar of cross-tenant access.

### Likelihood Explanation
Likelihood is high for any adversary who has installed the app on a shop they control (a normal, unprivileged action for anyone able to install a public/custom Shopify app), since:
- The app's `api_secret_key` is the same for every installing shop, so a valid HMAC obtained from one's own shop's webhook traffic is valid for any body content signed with that key.
- The `shop-domain` header is fully attacker-controlled at the HTTP layer and is never bound into the signed bytes, so no additional secret or privileged access is needed to rewrite it.
- No TLS interception, credential theft, or social engineering is required — only normal use of one's own app installation.

### Recommendation
Bind the tenant identity into the verified data instead of trusting an unauthenticated header:
- Include the shop domain (and other webhook-identifying headers such as topic/api-version/webhook-id) as part of the HMAC-signed input, or
- Independently corroborate `request.shop` against a value that is cryptographically tied to the specific installation (e.g., look up the session/access token for the claimed shop and confirm out-of-band that the webhook subscription for that shop id/topic actually exists), rather than trusting the header verbatim once only the body HMAC passes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, obtaining a legitimate app secret-signed webhook for any topic they choose to trigger (e.g. via `orders/create` on their own store), with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker crafts a POST request to the app's webhook endpoint using the same body `B` and same header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H` using the shared `api_secret_key`: [6](#0-5) 
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed_body(B), ...)`, so the host application processes attacker-chosen data under the victim shop's tenant context. [7](#0-6)

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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

**File:** test/webhooks/registry_test.rb (L14-33)
```ruby
        @shop = "shop.myshopify.com"

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
        @session = ShopifyAPI::Auth::Session.new(shop: ShopifyAPI::Context.host_name, access_token: "access_token")
        @url = "#{ShopifyAPI::Context.host}/admin/api/#{ShopifyAPI::Context.api_version}/graphql.json"
      end
```
