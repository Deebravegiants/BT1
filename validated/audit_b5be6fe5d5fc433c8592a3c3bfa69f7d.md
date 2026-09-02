## Title
Webhook `shop`, `topic`, `webhook_id` and `api_version` fields are trusted without being covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `Registry.process` and handed to the application's webhook handler are parsed straight out of unauthenticated HTTP headers. Anyone who can capture one legitimate `(raw_body, hmac)` pair for the shared app secret can replay it with a forged `shop-domain` (or `topic`) header, and `HmacValidator.validate` will still report success because it never checks those fields.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are read directly from headers and are not part of the signable string: [2](#0-1) 

`HmacValidator.validate` only checks `hmac` against `to_signable_string` (the body), so it never validates the headers: [3](#0-2) 

`Registry.process` trusts the HMAC check and then dispatches purely on `request.topic`, forwarding the unauthenticated `request.shop` straight to the application handler as `WebhookMetadata#shop`: [4](#0-3) 

Because the HMAC secret (the app's `client_secret`) is shared across every shop that installs the app, and the HMAC only binds the *body* bytes, the identity binding that should hold is:
`hmac(secret, raw_body) == received_hmac` **AND** `shop-domain header == shop that produced raw_body`.
This gem only enforces the first half. Any party who legitimately receives one webhook for their own (attacker-controlled) shop installation can capture a valid `raw_body` + `hmac`, then resend it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop and/or the `topic` header rewritten to any registered topic. `Utils::HmacValidator.validate` will accept it because the body/HMAC pair is genuine, and `Registry.process` will invoke the handler with `WebhookMetadata.shop` set to the forged victim shop domain.

### Impact Explanation
Applications built on this gem are expected to trust `WebhookMetadata#shop` (and `#topic`) to identify which tenant a webhook event belongs to — that's the entire purpose of the field being passed to the handler. Since the gem allows this value to be forged while the HMAC still validates, an attacker can inject or replay data under an arbitrary victim shop's identity, i.e. a cross-tenant access/data-injection scenario. This is Critical per the rules ("cross-tenant access").

### Likelihood Explanation
Exploitability only requires: (1) installing the target app on an attacker-controlled shop (unprivileged, standard merchant flow) to obtain one genuine `(raw_body, hmac)` sample signed with the app's shared secret, and (2) sending an HTTP POST to the app's webhook endpoint with that same body/hmac but a rewritten `x-shopify-shop-domain` (and optionally `x-shopify-topic`) header. No access to `api_secret_key`, tokens, or the victim's credentials is needed, matching the in-scope threat model.

### Recommendation
Include `shop`, `topic`, and any other header fields the handler relies on in the signed/verified material, or otherwise cryptographically bind them to the body (e.g., verify against Shopify's actual per-request signing scheme rather than trusting raw headers), before constructing `WebhookMetadata` in `Registry.process`. At minimum, document and/or verify that `shop-domain`/`topic` headers cannot be independently forged relative to the signed body.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; capture a genuine webhook POST, including its raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(client_secret, B)`).
2. Replay: `POST /webhooks` with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, still valid), but `x-shopify-shop-domain: victim.myshopify.com` and any registered `x-shopify-topic`.
3. `ShopifyAPI::Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` returns `true` (only `B`/`H` are checked).
4. `ShopifyAPI::Webhooks::Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches the handler with `shop: "victim.myshopify.com"`, even though the payload never originated from that shop.

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
