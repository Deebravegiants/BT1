## Finding

### Title
Webhook processing trusts the unauthenticated `X-Shopify-Shop-Domain`/`X-Shopify-Topic` headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then dispatches the handler using the `shop`, `topic`, `webhook_id`, and `api_version` values taken from HTTP headers that are **not** part of the signed material. Anyone who can obtain one valid `(raw_body, hmac)` pair — trivially available to any merchant who installs the app on their own store and receives a real webhook — can replay that exact body/HMAC combination to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header. The signature still validates, and the app attributes the (attacker-controlled) payload to a victim shop of the attacker's choosing.

### Finding Description
`Registry.process` does the following: [1](#0-0) 

The HMAC validation call goes through `Utils::HmacValidator.validate`, which computes the signature purely from `verifiable_query.to_signable_string`: [2](#0-1) 

For webhook requests, `to_signable_string` returns only the raw body — none of the identifying headers are included: [3](#0-2) 

`request.shop`, `request.topic`, and `request.webhook_id` are all read straight from attacker-suppliable HTTP headers with no cryptographic binding to the HMAC: [4](#0-3) 

The equality the library implicitly (and incorrectly) assumes is:
`HMAC_valid(raw_body) == true` implies `request.shop == "the shop that actually sent this payload"`.

In reality the HMAC only proves "this body was produced by someone holding `api_secret_key` (i.e., Shopify) at some point" — it says nothing about which shop the body belongs to, nor which shop header should be trusted. Since `shop`, `topic`, and `webhook_id` live outside the signed string, any party capable of producing (or replaying) a valid `(body, hmac)` pair — including a legitimate merchant using the app on their own store, who legitimately receives real, correctly-signed webhooks from Shopify for their own shop — can resend that same body/HMAC pair to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header naming a different, victim shop.

### Impact Explanation
`Registry.process` passes the spoofed `shop` value straight into the handler: [5](#0-4) 

Because host applications key their persisted data (orders, inventory changes, uninstall events, GDPR-relevant customer data, etc.) by `data.shop`, this allows an attacker to inject or spoof events under another merchant's tenant identity — a cross-tenant data injection that breaks the shop-identity boundary the HMAC is meant to enforce. This satisfies the "Critical – cross-tenant access" impact bar: the shop that is cryptographically authenticated (implicitly, "whoever holds a valid body/HMAC pair") is not equal to the shop the code trusts and stores data against (`request.shop` from an unauthenticated header).

### Likelihood Explanation
No possession of `api_secret_key`, an access token, or any privileged credential is required. Any ordinary merchant who has installed the target app on their own store legitimately receives properly-HMAC-signed webhooks from Shopify for their own shop. That merchant can capture one such `(raw_body, hmac)` pair (e.g. via browser dev tools/network proxy on their own traffic, which is completely within their rights as the resource owner) and replay it to the app's public webhook endpoint with a forged `shop-domain` header. This requires only network access to the app's publicly reachable webhook URL — a routine unprivileged-internet-user capability.

### Recommendation
Include the identifying headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material, or otherwise cryptographically bind them (e.g., require that the app independently confirm, via an authenticated API call using a stored access token for the claimed shop, that the webhook is plausible) before trusting `request.shop`/`request.topic` for any tenant-scoped action. At minimum, document prominently that these header values are unauthenticated and must not be trusted as tenant keys without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and lets Shopify deliver a real webhook (e.g. `orders/create`) to the app's public endpoint. Attacker captures the raw request body `B` and the `X-Shopify-Hmac-Sha256` header value `H` (a valid HMAC of `B` under the app's real `api_secret_key`, computed by Shopify).
2. Attacker crafts a new HTTP POST to the same public webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid because it only signs `B`)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - Header `X-Shopify-Topic: orders/create` (unchanged or forged)
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and successfully matches `H`, so the request is accepted.
4. The webhook handler is invoked with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from, and pertains to, `attacker-shop.myshopify.com`, letting the attacker inject/spoof data under the victim shop's tenant identity in the host application.

### Citations

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
