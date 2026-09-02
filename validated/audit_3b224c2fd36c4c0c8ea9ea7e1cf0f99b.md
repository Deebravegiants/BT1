I have sufficient evidence now to write up the finding.

### Title
Webhook `shop-domain`, `topic`, `api-version`, and `webhook-id` headers are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Webhooks::Registry.process` accepts any request whose body/HMAC pair validates against the app's `client_secret`. The `shop`, `topic`, `api_version`, and `webhook_id` values are read straight from unauthenticated HTTP headers and passed on to the app's handler, with `topic` also used to select *which* handler runs. None of these fields are covered by the HMAC, so the "this webhook body came from shop X for topic Y" binding is not actually enforced by the signature.

### Finding Description
`Request#hmac` decodes the `X-Shopify-Hmac-Sha256`/`shopify-hmac-sha256` header, and `Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all pulled from headers that are not part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC (body-only) and then uses the unauthenticated `topic` header to pick the handler to invoke, and forwards the unauthenticated `shop`, `webhook_id`, and `api_version` values straight into `WebhookMetadata` given to the handler: [3](#0-2) 

`HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` (the raw body for webhooks) against the secret — it has no knowledge of `shop`, `topic`, or the other headers: [4](#0-3) 

The identity binding broken is: `HMAC(client_secret, raw_body) valid` is treated as equivalent to `shop == request.shop AND topic == request.topic`, when in fact the HMAC only proves `raw_body` was produced with the shared `client_secret` — it says nothing about which shop or topic the body belongs to.

Because `client_secret` is the app's client secret (shared across every shop that installs the app, not shop-specific), any merchant who installs the app on their own store legitimately receives real webhook deliveries signed with that same secret. Such a user can capture a legitimately-signed `(raw_body, hmac)` pair from their own shop's webhook delivery, then replay it to the app's public webhook endpoint while altering the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, and `shopify-api-version` headers (which are not covered by the signature) to claim the payload originated from a different shop and/or a different topic. `Registry.process` will still validate the HMAC (since the body/secret pair is genuine) and will happily route the attacker-supplied body to the handler for the forged topic under the forged shop identity.

### Impact Explanation
This breaks the cross-tenant isolation the HMAC check is meant to provide: a party controlling one shop (unprivileged relative to any other tenant, and requiring no `api_secret_key`, access token, or victim credentials) can inject data into the host application's webhook handling pipeline while impersonating a different shop, or route data intended for one topic into the handler for a more sensitive topic (e.g. `shop/redact`, `customers/data_request`, `app/uninstalled`). Depending on what the host application's `WebhookHandler` implementation does with `data.shop`/`data.topic` (as documented, apps are expected to trust and act on these fields), this can lead to cross-tenant data corruption, spoofed compliance/redaction webhooks, or forced execution of privileged app-lifecycle handlers under an arbitrary shop identity.

### Likelihood Explanation
Exploitation only requires: (1) being any merchant who can install the target app (no special privilege, no access to `api_secret_key` or another shop's tokens), and (2) the ability to intercept/replay the raw HTTP request sent to the app's own webhook endpoint, which is attacker-controlled infrastructure to begin with. No cryptographic secret needs to be recovered — the attacker reuses a legitimate signature they were validly given for their own body/secret pair and only tampers with header fields that were never part of the signed content.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the HMAC-signable string for webhook requests (mirroring how `Auth::Oauth::AuthQuery` binds `code`, `host`, `shop`, `state`, and `timestamp` into `to_signable_string`), so that tampering with any of these header-derived fields invalidates the signature. At minimum, `topic` (used for handler dispatch) and `shop` (used as the tenant identity forwarded to handlers) must be cryptographically bound to the signature, not merely read from unauthenticated headers.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a real webhook delivery for a low-sensitivity topic, capturing the raw body `B` and the valid `shopify-hmac-sha256` header `H = HMAC-SHA256(client_secret, B)`.
2. Attacker POSTs to the app's public webhook endpoint with:
   - `raw_body: B`
   - `shopify-hmac-sha256: H` (unchanged, still valid since body is unchanged)
   - `shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - `shopify-topic: shop/redact` (forged to a mandatory/sensitive topic if the same `add_registration` handler exists)
3. The host app calls:
```ruby
ShopifyAPI::Webhooks::Registry.process(
  ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: attacker_headers)
)
```
4. `Utils::HmacValidator.validate(request)` returns `true` because it only checks `B` against `H` and `client_secret`, per [5](#0-4) .
5. `Registry.process` looks up the handler for the forged `shop/redact` topic and invokes it with `shop: "victim-shop.myshopify.com"` and the attacker's body `B`, per [6](#0-5) , even though `B` was never actually produced by or for `victim-shop.myshopify.com`.

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
