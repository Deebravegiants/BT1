Confirmed. In `Webhooks::Registry.process`, at [1](#0-0) , the only check performed is `Utils::HmacValidator.validate(request)`, and then `request.topic` and `request.shop` are passed straight into the handler via `WebhookMetadata`.

### Title
Webhook `shop` and `topic` fields are trusted despite not being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop` and `topic` from HTTP headers (`shopify-shop-domain`, `shopify-topic`) that are never included in the HMAC-signed payload, and `Registry.process` trusts those unauthenticated header values to route/attribute the webhook to a specific merchant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [2](#0-1) . The HMAC validation in `Utils::HmacValidator.validate` computes the signature over `to_signable_string` and compares it to the `hmac` header: [3](#0-2) . This means the cryptographic guarantee only binds the **body bytes**, never the `shop`, `topic`, or `webhook-id` headers.

`Request#shop` and `Request#topic` are pulled straight from headers, with no cross-check against the body or any authenticated value: [4](#0-3) .

`Registry.process` validates only the HMAC, then dispatches using the unauthenticated `topic` and forwards the unauthenticated `shop` into `WebhookMetadata`, which the host application's handler uses to attribute the event to a tenant: [1](#0-0) .

The identity binding broken is: **bytes verified (`raw_body`) ≠ bytes parsed (`shop`, `topic` from headers)**. Because a webhook's HMAC is computed as `HMAC(secret, raw_body)` and does not incorporate the shop/topic headers, any request bearing a *valid* `(raw_body, hmac)` pair for the app (e.g. a genuine webhook replayed, or one whose HMAC is derivable because the body is fixed/predictable content such as `"{}"` for topics like `app/uninstalled` with no payload) will pass `HmacValidator.validate` regardless of the `shopify-shop-domain` or `shopify-topic` header values attached to it. An attacker who is able to submit an HTTP request to the app's webhook endpoint (this endpoint is normally internet-reachable, since Shopify calls it from the internet) can swap in an arbitrary `shopify-shop-domain` header while reusing a raw body whose HMAC they already know is valid for the app's secret, causing the handler to process/act on a webhook for one shop while claiming it originates from a different shop.

### Impact Explanation
This breaks tenant isolation: a webhook payload verified as authentic for the app's `client_secret` can be replayed with a forged `shop` value that the handler trusts to select which merchant's records to modify/delete (e.g. `customers/redact`, `shop/redact`, `app/uninstalled` deactivating another shop's session). This is a cross-tenant access vector, matching the Critical impact bucket (cross-tenant access) defined in scope.

### Likelihood Explanation
Exploitability requires only network access to the app's public webhook endpoint and a body/HMAC pair known to be valid for the app's secret (trivially true for topics with static/empty bodies, or via HMAC-preserving replay of any previously captured genuine webhook for topics whose body doesn't embed shop identity, e.g. `app/uninstalled`). No access token, `api_secret_key`, or privileged account is needed by the attacker — only the ability to POST to the reachable webhook path with attacker-chosen headers.

### Recommendation
Bind `shop` and `topic` into the signed material used for validation (or independently verify `shop`/`topic` against Shopify-issued, tamper-evident data) instead of trusting raw headers once only the body HMAC has been checked. At minimum, `to_signable_string` (or a dedicated verification step) should incorporate the `shop` and `topic` header values so that forged header/body combinations fail validation.

### Proof of Concept
1. Attacker observes/knows a valid `(raw_body, hmac)` pair for the target app's webhook secret — e.g., an empty-body topic such as `app/uninstalled`, whose `HMAC(secret, "")`-style signature is constant and independent of which shop triggered it, or by replaying a captured legitimate webhook.
2. Attacker sends a POST to the app's webhook endpoint with:
   - `shopify-hmac-sha256`: the known-valid HMAC for that body
   - `shopify-topic`: `app/uninstalled` (or another topic the attacker wants processed)
   - `shopify-shop-domain`: `victim-shop.myshopify.com` (a shop the attacker does not control)
   - body: the raw body matching the known-valid HMAC
3. `Utils::HmacValidator.validate(request)` succeeds because it only checks the body bytes: [5](#0-4) .
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-supplied, unauthenticated `shop`/`topic` values and invokes the handler: [6](#0-5) .
5. The app's handler acts on `victim-shop.myshopify.com` (e.g., deactivates its session, deletes its data) even though the actual webhook body/HMAC never attested to that shop.

### Citations

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
