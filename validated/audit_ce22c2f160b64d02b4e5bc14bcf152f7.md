## Finding

Webhook authenticity in this gem is verified via `ShopifyAPI::Utils::HmacValidator.validate`, which computes the HMAC only over the value returned by `to_signable_string`. For webhooks, `ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

But the `shop` (and `topic`) values that are used to attribute and route the incoming webhook are pulled straight from unauthenticated HTTP headers, outside the HMAC-covered content: [2](#0-1) 

`Registry.process` validates the HMAC using only the body, then dispatches the handler keyed by the unauthenticated `topic` header and passes the unauthenticated `shop` header straight into the handler metadata: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` compute and compare the digest solely against `verifiable_query.to_signable_string` (the raw body for webhooks), never incorporating the `shop-domain` or `topic` headers into the signed material: [4](#0-3) 

### Title
Webhook `shop`/`topic` attribution is not bound by the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic for a given `shop` and `topic` as long as `HmacValidator.validate` succeeds, but that validation only proves the *body* bytes were signed with the app's shared `client_secret` — it proves nothing about which shop or topic the signer intended. Because the `client_secret`/HMAC key is shared across every merchant that installs the app (it is not per-tenant), any merchant who has legitimately installed the app can capture one of their own genuinely Shopify-signed webhook deliveries (`raw_body` + `X-Shopify-Hmac-Sha256`) and replay it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header pointing at a different, victim shop. `HmacValidator.validate` will still return `true` because it never inspected those headers, and `Registry.process` will hand the attacker-controlled body to the handler labeled as data belonging to the victim shop.

### Finding Description
The vulnerable invariant should be: `hmac_is_valid(request) == true` implies `(shop, topic, body)` as a whole were authenticated by Shopify. Instead the gem only enforces `hmac_is_valid(body) == true`, i.e. the equality actually verified is `HMAC(body, client_secret) == received_hmac`, while `shop` and `topic` are trusted unconditionally from headers that carry no cryptographic binding to the signature. This is the same class of bug as the referenced Cairo report: a value that is *used* downstream (there: message status; here: tenant/topic attribution) is not actually covered by the check that is supposed to guarantee its integrity.

Because the app-level HMAC secret (`Context.api_secret_key`) is identical for all shops that install a given app — it is the app's `client_secret`, not a per-shop secret — a request that is "signed" for one tenant is indistinguishable, at the HMAC layer, from a request "signed" for any other tenant. Any party who can install the app on their own store (an unprivileged internet user with respect to any other merchant's data) can obtain body+HMAC pairs that are valid under this shared key and then relabel them as belonging to a different shop.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce: `Registry.process` will hand attacker-supplied webhook payloads to the application's registered handler tagged with an arbitrary victim `shop` domain and arbitrary `topic`, since neither is authenticated. Any host application that keys persistence, authorization, or session lookups off `WebhookMetadata#shop`/`#topic` (as the gem's own webhook documentation instructs) can be made to write or act on data under another tenant's identity — a cross-tenant access impact.

### Likelihood Explanation
Exploitation only requires being an app user (installing the target app on one's own development/trial store is typically self-serve) capable of receiving at least one real webhook, then replaying that exact body with a modified `shop`/`topic` header to the app's public webhook endpoint. No access to `api_secret_key`, no privileged account, and no TLS interception are needed — only observation of one's own legitimately received webhook traffic.

### Recommendation
Bind the identity fields into the authenticated material, or otherwise require the caller to attest that the header values were verified against the actual delivering source (e.g., ship a helper that requires an out-of-band trusted transport, or fold `shop`/`topic` into the value passed to `HmacValidator` so `to_signable_string` incorporates them, rejecting mismatches). At minimum, document prominently that `shop`/`topic` in `WebhookMetadata` are not covered by HMAC verification and must not be trusted for tenant attribution without additional binding (e.g., cross-checking against a known list of `shop`s that have completed OAuth for this app).

### Proof of Concept
1. Merchant A installs the target Shopify app on `attacker-shop.myshopify.com` (a shop they control) and lets Shopify deliver a real webhook, capturing `raw_body`, `X-Shopify-Hmac-Sha256`, and `X-Shopify-Topic`.
2. Merchant A POSTs that exact `raw_body`/`X-Shopify-Hmac-Sha256` pair to the same app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers (no shop-hmac binding check) at `lib/shopify_api/webhooks/request.rb`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(raw_body, api_secret_key)` and matches the header — succeeding, because `api_secret_key` is shared across the app's installs, not scoped to `attacker-shop`.
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: request.topic, body: request.parsed_body, ...)`, causing the host app to process attacker-controlled data as though it originated from `victim-shop.myshopify.com`.

### Citations

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
